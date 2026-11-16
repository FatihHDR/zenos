"""Phase 4: time-to-first-token (TTFT) measurement for the streaming pipeline."""

import statistics
import time
from typing import Any, Dict, List, Tuple


def measure_ttft_with_context(
    pipeline: Any, query: str
) -> Tuple[Dict[str, Any], List[Any]]:
    """Run one full turn and return both the TTFT row and the context chunks.

    The context chunks are returned alongside the row because grounding metrics need
    them to validate the citation tags found in the answer (a tag is only valid when it
    points at a chunk that was really supplied).  ``measure_ttft`` is the row-only
    convenience wrapper.

    The timer starts *before* retrieval, so ``ttft_ms`` covers
    retrieve + rerank + time-to-first-token (matching the PRD definition of the
    user-perceived latency). Retrieval/rerank run when ``answer_streaming``
    builds the generator; the model call happens on first iteration.
    """
    start = time.perf_counter()
    reranked, stream = pipeline.answer_streaming(query)
    retrieval_ms = (time.perf_counter() - start) * 1000

    first_token_ms = None
    parts: List[str] = []
    for delta in stream:
        if first_token_ms is None:
            first_token_ms = (time.perf_counter() - start) * 1000
        parts.append(delta)
    total_ms = (time.perf_counter() - start) * 1000

    text = "".join(parts)
    answer = pipeline.generator.finalize(query, reranked, text)

    row = {
        "query": query,
        "ttft_ms": first_token_ms if first_token_ms is not None else total_ms,
        "retrieval_ms": retrieval_ms,
        "generation_ms": total_ms - retrieval_ms,
        "total_ms": total_ms,
        "grounded": answer.grounded,
        "refused": answer.refused,
        "num_contexts": len(reranked),
        "answer": text,
    }
    return row, list(reranked)


def measure_ttft(pipeline: Any, query: str) -> Dict[str, Any]:
    """Measure TTFT and total latency for one query."""
    row, _ = measure_ttft_with_context(pipeline, query)
    return row


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = min(len(sorted_values) - 1, int(round(p * (len(sorted_values) - 1))))
    return sorted_values[idx]


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    """p50/p95/max/mean TTFT (and retrieval time) across measured queries."""
    ttft = sorted(r["ttft_ms"] for r in rows)
    retrieval = sorted(r["retrieval_ms"] for r in rows)
    if not ttft:
        return {
            "count": 0,
            "ttft_p50_ms": 0.0,
            "ttft_p95_ms": 0.0,
            "ttft_max_ms": 0.0,
            "ttft_mean_ms": 0.0,
            "retrieval_mean_ms": 0.0,
        }
    return {
        "count": len(ttft),
        "ttft_p50_ms": _percentile(ttft, 0.50),
        "ttft_p95_ms": _percentile(ttft, 0.95),
        "ttft_max_ms": ttft[-1],
        "ttft_mean_ms": statistics.fmean(ttft),
        "retrieval_mean_ms": statistics.fmean(retrieval),
    }
