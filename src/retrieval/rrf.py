"""Reciprocal Rank Fusion (RRF) engine.

This module implements the Reciprocal Rank Fusion algorithm used by Phase 2 of
Zenos to combine the rankings of a semantic (dense) search and an exact/lexical
(sparse / BM25) search into a single, normalized ranking.

The classic RRF formulation (Cormack et al., 2009) scores a document ``d`` as::

    RRF(d) = sum_i  w_i * 1 / (k + rank_i(d))

where ``rank_i(d)`` is the 1-based position of ``d`` in the i-th result list and
``k`` is a smoothing constant (60 by convention) that dampens the influence of
top ranks so that a document that is *consistently* mid-ranked can still beat a
document that only tops a single list.

Qdrant applies the very same formula server-side (see
``QdrantManager.search_hybrid_rrf`` with ``models.Fusion.RRF``).  This pure-Python
implementation is intentionally dependency-free so that:

* the fusion logic can be unit-tested without a running Qdrant instance, and
* client-side fusion stays available as a fallback and as an independent
  cross-check of the database-level implementation.
"""

from collections import OrderedDict
from typing import Callable, Dict, Hashable, List, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")

#: Default RRF smoothing constant, as recommended in the original paper.
DEFAULT_RRF_K: int = 60


def rrf_score(rank: int, k: int = DEFAULT_RRF_K) -> float:
    """Return the RRF contribution of a single document at ``rank`` (1-based)."""
    if rank < 1:
        raise ValueError("rank must be 1-based (>= 1)")
    if k < 0:
        raise ValueError("k must be >= 0")
    return 1.0 / (k + rank)


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[T]],
    k: int = DEFAULT_RRF_K,
    weights: Optional[Sequence[float]] = None,
    key: Optional[Callable[[T], Hashable]] = None,
) -> List[Tuple[T, float, Dict[int, int]]]:
    """Fuse several ranked result lists using Reciprocal Rank Fusion.

    Args:
        ranked_lists: One ranked sequence per retriever, best-first.  Duplicate
            items inside a single list are only counted once (best rank wins).
        k: RRF smoothing constant (default 60 from the original paper).
        weights: Optional per-list weights.  When omitted every list is weighted
            equally (1.0).  Length must match ``ranked_lists``.
        key: Optional function returning a hashable identity for an item.  When
            omitted the item itself is used as the dictionary key.

    Returns:
        A list of ``(item, fused_score, provenance)`` tuples sorted by fused
        score descending.  ``provenance`` maps the index of each contributing
        list to the 1-based rank the item held in that list, which is what the
        evaluation harness uses to report dense/sparse contribution.
    """
    if k < 0:
        raise ValueError("k must be >= 0")

    if weights is None:
        weights = [1.0] * len(ranked_lists)
    if len(weights) != len(ranked_lists):
        raise ValueError(
            f"weights length ({len(weights)}) must match ranked_lists length "
            f"({len(ranked_lists)})"
        )

    key_fn: Callable[[T], Hashable] = key or (lambda item: item)  # type: ignore[assignment]

    scores: Dict[Hashable, float] = {}
    provenance: Dict[Hashable, Dict[int, int]] = {}
    first_seen: "OrderedDict[Hashable, T]" = OrderedDict()

    for list_idx, ranked in enumerate(ranked_lists):
        weight = weights[list_idx]
        for position, item in enumerate(ranked, start=1):
            item_key = key_fn(item)
            if item_key not in first_seen:
                first_seen[item_key] = item
                scores[item_key] = 0.0
                provenance[item_key] = {}
            # A duplicated item keeps its best (smallest) rank within the list.
            if list_idx in provenance[item_key]:
                continue
            provenance[item_key][list_idx] = position
            scores[item_key] += weight * rrf_score(position, k=k)

    # Deterministic ordering: fused score desc, then best individual rank asc,
    # then insertion order (stable across runs for reproducible evaluation).
    def sort_key(item_key: Hashable) -> Tuple[float, int, int]:
        prov = provenance[item_key]
        best_rank = min(prov.values()) if prov else 10**9
        order = list(first_seen).index(item_key)
        return (-scores[item_key], best_rank, order)

    fused_keys = sorted(first_seen.keys(), key=sort_key)
    return [
        (first_seen[item_key], scores[item_key], provenance[item_key])
        for item_key in fused_keys
    ]
