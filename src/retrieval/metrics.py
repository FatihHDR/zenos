"""Retrieval evaluation metrics for Phase 2 (Recall accuracy on top-25 candidates)."""

from typing import Iterable, List, Optional, Sequence


def recall_at_k(
    retrieved: Sequence[str],
    relevant: Iterable[str],
    k: Optional[int] = None,
) -> float:
    """Compute Recall@k: the fraction of *relevant* items found in the top-k.

    Args:
        retrieved: Chunk (or doc) ids in ranking order, best first.
        relevant: The set of ids considered relevant for the query.
        k: Size of the prefix of ``retrieved`` to consider.  Defaults to the
            full length of ``retrieved``.

    Returns:
        Value in ``[0.0, 1.0]``.  Returns ``0.0`` when no relevant ids exist.
        When ``k=0`` returns ``0.0``.
    """
    if k is None:
        k = len(retrieved)
    k = max(0, min(k, len(retrieved)))
    if k == 0:
        return 0.0

    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0

    found = sum(1 for item in retrieved[:k] if item in relevant_set)
    return found / len(relevant_set)


def precision_at_k(
    retrieved: Sequence[str],
    relevant: Iterable[str],
    k: Optional[int] = None,
) -> float:
    """Compute Precision@k: the fraction of the top-k that is relevant."""
    if k is None:
        k = len(retrieved)
    k = max(0, min(k, len(retrieved)))
    if k == 0:
        return 0.0
    relevant_set = set(relevant)
    found = sum(1 for item in retrieved[:k] if item in relevant_set)
    return found / k


def mean_recall_at_k(
    evaluations: Sequence[dict],
    k: int,
) -> float:
    """Average Recall@k across a list of ``{retrieved: [...], relevant: [...]}`` dicts."""
    if not evaluations:
        return 0.0
    total = sum(
        recall_at_k(ev["retrieved"], ev["relevant"], k=k) for ev in evaluations
    )
    return total / len(evaluations)


def format_recall_report(evaluations: Sequence[dict], k: int = 25) -> str:
    """Pretty-print a human-readable Recall@k report per query."""
    lines = [
        f"{'Query':<60} {'Recall@' + str(k):<12} {'Hits':<6} {'#Rel':<5}",
        "-" * 95,
    ]
    for ev in evaluations:
        q = ev.get("query", "")[:58]
        r = recall_at_k(ev["retrieved"], ev["relevant"], k=k)
        hits = sum(1 for x in ev["retrieved"][:k] if x in set(ev["relevant"]))
        lines.append(
            f"{q:<60} {r:<12.3f} {hits:<6} {len(ev['relevant']):<5}"
        )
    return "\n".join(lines)