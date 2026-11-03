"""Phase 4: evaluation (Ragas metrics + TTFT measurement)."""

from evaluation.ragas_eval import (
    build_eval_records,
    compute_context_relevance,
    compute_recall_at_k,
    run_ragas,
)
from evaluation.ttft import measure_ttft, summarize

__all__ = [
    "build_eval_records",
    "compute_context_relevance",
    "compute_recall_at_k",
    "run_ragas",
    "measure_ttft",
    "summarize",
]
