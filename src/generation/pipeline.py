"""End-to-end Phase 3 pipeline: hybrid retrieval -> rerank -> grounded generation."""

import logging
from typing import List, Optional, Tuple

from config import settings
from db.qdrant import HybridSearchResult, QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor
from generation.generator import GroundedGenerator
from models import GroundedAnswer
from reranking.reranker import BaseReranker, RerankResult, get_reranker

logger = logging.getLogger(__name__)


class GroundedQAPipeline:
    """Orchestrates hybrid retrieval, cross-encoder reranking, and cited generation."""

    def __init__(
        self,
        db_manager: Optional[QdrantManager] = None,
        extractor: Optional[BGEM3EmbeddingExtractor] = None,
        reranker: Optional[BaseReranker] = None,
        generator: Optional[GroundedGenerator] = None,
        candidates: Optional[int] = None,
        top_n: Optional[int] = None,
    ):
        self.db_manager = db_manager or QdrantManager()
        self.extractor = extractor or BGEM3EmbeddingExtractor()
        self.reranker = reranker or get_reranker()
        self.generator = generator or GroundedGenerator()
        self.candidates = candidates or settings.retrieval_candidates
        self.top_n = top_n or settings.rerank_top_n

    def retrieve(self, query: str) -> List[HybridSearchResult]:
        """Run database-level hybrid (dense + sparse RRF) search for the candidate pool."""
        dense_vec, sparse = self.extractor.embed_query(query)
        return self.db_manager.search_hybrid_rrf(
            query_vector=dense_vec,
            sparse_indices=sparse.indices,
            sparse_values=sparse.values,
            limit=self.candidates,
        )

    def answer_with_context(self, query: str) -> Tuple[List[RerankResult], GroundedAnswer]:
        """Like :meth:`answer` but also returns the reranked chunks used as context."""
        candidates = self.retrieve(query)
        reranked = self.reranker.rerank(query, candidates, top_n=self.top_n)
        return reranked, self.generator.generate(query, reranked)

    def answer(self, query: str) -> GroundedAnswer:
        """Retrieve, rerank to ``top_n``, and generate a cited answer."""
        return self.answer_with_context(query)[1]
