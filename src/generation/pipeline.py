"""End-to-end Phase 3 pipeline: hybrid retrieval -> rerank -> grounded generation."""

import logging
from typing import Iterator, List, Optional, Tuple

from config import settings
from db.qdrant import HybridSearchResult, QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor
from generation.generator import GroundedGenerator
from models import GroundedAnswer
from reranking.reranker import BaseReranker, RerankResult, get_reranker

logger = logging.getLogger(__name__)


class GroundedQAPipeline:
    """Orchestrates hybrid retrieval, cross-encoder reranking, and cited generation."""

    RETRIEVAL_MODES = ("dense", "sparse", "hybrid")

    def __init__(
        self,
        db_manager: Optional[QdrantManager] = None,
        extractor: Optional[BGEM3EmbeddingExtractor] = None,
        reranker: Optional[BaseReranker] = None,
        generator: Optional[GroundedGenerator] = None,
        candidates: Optional[int] = None,
        top_n: Optional[int] = None,
        retrieval_mode: Optional[str] = None,
        rerank: Optional[bool] = None,
    ):
        self.db_manager = db_manager or QdrantManager()
        self.extractor = extractor or BGEM3EmbeddingExtractor()

        self.retrieval_mode = (retrieval_mode or settings.retrieval_mode).lower()
        if self.retrieval_mode not in self.RETRIEVAL_MODES:
            raise ValueError(
                f"Unknown retrieval mode {self.retrieval_mode!r}. "
                f"Expected one of {self.RETRIEVAL_MODES}."
            )

        self.rerank = settings.rerank_enabled if rerank is None else rerank
        # Skipping the reranker must also skip loading the cross-encoder: it costs
        # ~2 GB of RAM, which is the difference between running and being OOM-killed.
        self.reranker = reranker or (get_reranker() if self.rerank else None)
        self.generator = generator or GroundedGenerator()
        self.candidates = candidates or settings.retrieval_candidates
        self.top_n = top_n or settings.rerank_top_n

    def retrieve(self, query: str) -> List[HybridSearchResult]:
        """Search the candidate pool using the configured retrieval mode."""
        dense_vec, sparse = self.extractor.embed_query(query)

        if self.retrieval_mode == "dense":
            return self.db_manager.search_dense(
                query_vector=dense_vec,
                limit=self.candidates,
            )
        if self.retrieval_mode == "sparse":
            return self.db_manager.search_sparse(
                sparse_indices=sparse.indices,
                sparse_values=sparse.values,
                limit=self.candidates,
            )
        return self.db_manager.search_hybrid_rrf(
            query_vector=dense_vec,
            sparse_indices=sparse.indices,
            sparse_values=sparse.values,
            limit=self.candidates,
        )

    def select_context(
        self,
        query: str,
        candidates: List[HybridSearchResult],
    ) -> List[RerankResult]:
        """Reduce the candidate pool to the chunks handed to the generator.

        Reranking on: the cross-encoder's top-``top_n``.  Reranking off: the
        top-``top_n`` of the retrieval/fusion ranking passed straight through.
        """
        if self.rerank:
            return self.reranker.rerank(query, candidates, top_n=self.top_n)

        return [
            RerankResult(
                chunk_id=candidate.chunk_id,
                text=candidate.text,
                score=float(candidate.score),
                original_score=float(candidate.score),
                payload=candidate.payload,
            )
            for candidate in candidates[: self.top_n]
        ]

    def answer_with_context(self, query: str) -> Tuple[List[RerankResult], GroundedAnswer]:
        """Like :meth:`answer` but also returns the chunks used as context."""
        candidates = self.retrieve(query)
        context = self.select_context(query, candidates)
        return context, self.generator.generate(query, context)

    def answer(self, query: str) -> GroundedAnswer:
        """Retrieve, reduce to ``top_n``, and generate a cited answer."""
        return self.answer_with_context(query)[1]

    def answer_streaming(self, query: str) -> Tuple[List[RerankResult], Iterator[str]]:
        """Retrieve, reduce to ``top_n``, and stream the answer deltas (for TTFT / progressive UI)."""
        candidates = self.retrieve(query)
        context = self.select_context(query, candidates)
        return context, self.generator.stream(query, context)
