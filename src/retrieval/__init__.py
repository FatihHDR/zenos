"""Phase 2: Hybrid Search & Fusion Implementation.

This package contains the parallel retriever modules built on LlamaIndex
(``llama_retrievers``), the database-level Reciprocal Rank Fusion search exposed
on :class:`~db.qdrant.QdrantManager`, the pure-Python RRF engine (``rrf``), and
the Recall@25 evaluation harness (``metrics`` / ``evaluate``).
"""

from retrieval.llama_retrievers import (
    DenseRetriever,
    LlamaIndexRRFRetriever,
    SparseRetriever,
)
from retrieval.rrf import reciprocal_rank_fusion

__all__ = [
    "DenseRetriever",
    "SparseRetriever",
    "LlamaIndexRRFRetriever",
    "reciprocal_rank_fusion",
]