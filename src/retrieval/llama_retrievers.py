"""Parallel retriever modules built on LlamaIndex for hybrid search.

Phase 2 of the PRD calls for two things:

1.  *"Build parallel retriever modules using LlamaIndex."*  We implement a
    dense (semantic) retriever and a sparse (exact/BM25) retriever as thin
    LlamaIndex ``BaseRetriever`` subclasses backed by a
    :class:`llama_index.vector_stores.qdrant.QdrantVectorStore`.  Both are
    queryable in isolation (``retrieve("...")``) and in parallel.
2.  *"Apply the Reciprocal Rank Fusion (RRF) algorithm at the database level"*
    — the canonical implementation of this lives in
    ``QdrantManager.search_hybrid_rrf`` using Qdrant's native
    ``FusionQuery(prefetch=[...], fusion=Fusion.RRF)``.  The
    :class:`LlamaIndexRRFRetriever` exposed here is a LlamaIndex-compatible
    facade over that same database-level search, so the rest of the LlamaIndex
    ecosystem (query engines, evaluations) can consume fused results as regular
    ``NodeWithScore`` objects.

Sparse query embedding uses the same ``BAAI/bge-m3`` model as ingestion (through
FastEmbed), guaranteeing that query tokens live in the same vocabulary/dimension
as the indexed sparse vectors.
"""

import logging
from typing import List, Optional, Sequence

from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.vector_stores.types import (
    MetadataFilters,
    VectorStoreQuery,
    VectorStoreQueryMode,
)
from llama_index.core.vector_stores import VectorStoreQueryResult
from llama_index.vector_stores.qdrant import QdrantVectorStore

from config import settings
from db.qdrant import QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sparse encoder helpers shared with the QdrantVectorStore
# ---------------------------------------------------------------------------
def sparse_bge_m3_encoder(extractor: BGEM3EmbeddingExtractor):
    """Return a FastEmbed-style ``(indices, values)`` callable for a query string.

    ``QdrantVectorStore`` expects a ``SparseEncoderCallable`` of the form
    ``fn(texts: List[str]) -> Tuple[List[List[int]], List[List[float]]]``. We
    adapt our existing BGE-M3 extractor so the vector store can compute sparse
    query vectors with *the same* model used during ingestion.
    """

    def compute_vectors(texts: List[str]):
        _, sparse_vecs = extractor.embed_texts(texts, batch_size=len(texts) or 1)
        indices = [s.indices for s in sparse_vecs]
        values = [s.values for s in sparse_vecs]
        return indices, values

    return compute_vectors


class DenseRetriever(BaseRetriever):
    """LlamaIndex retriever performing pure dense (semantic) vector search."""

    def __init__(
        self,
        vector_store: Optional[QdrantVectorStore] = None,
        extractor: Optional[BGEM3EmbeddingExtractor] = None,
        similarity_top_k: int = 25,
        filters: Optional[MetadataFilters] = None,
    ):
        self._vector_store = vector_store or self._default_vector_store(extractor)
        self._extractor = extractor or BGEM3EmbeddingExtractor()
        self._similarity_top_k = similarity_top_k
        self._filters = filters
        super().__init__()

    @staticmethod
    def _default_vector_store(extractor: Optional[BGEM3EmbeddingExtractor]):
        extractor = extractor or BGEM3EmbeddingExtractor()
        return QdrantVectorStore(
            collection_name=settings.qdrant_collection_name,
            client=QdrantManager().client,
            enable_hybrid=False,
        )

    def _retrieve(self, query_bundle) -> Sequence[NodeWithScore]:
        query_str = query_bundle.query_str
        dense_vec, _ = self._extractor.embed_query(query_str)
        query = VectorStoreQuery(
            query_embedding=dense_vec,
            similarity_top_k=self._similarity_top_k,
            mode=VectorStoreQueryMode.DEFAULT,
            filters=self._filters,
        )
        result: VectorStoreQueryResult = self._vector_store.query(query)
        return self._to_nodes(result)

    @staticmethod
    def _to_nodes(result: VectorStoreQueryResult) -> List[NodeWithScore]:
        nodes: List[NodeWithScore] = []
        for node, score in zip(result.nodes, result.similarities):
            nodes.append(NodeWithScore(node=node, score=score))
        return nodes


class SparseRetriever(BaseRetriever):
    """LlamaIndex retriever performing pure sparse (exact / BM25) search."""

    def __init__(
        self,
        vector_store: Optional[QdrantVectorStore] = None,
        extractor: Optional[BGEM3EmbeddingExtractor] = None,
        similarity_top_k: int = 25,
        filters: Optional[MetadataFilters] = None,
    ):
        self._vector_store = vector_store or self._default_vector_store(extractor)
        self._extractor = extractor or BGEM3EmbeddingExtractor()
        self._similarity_top_k = similarity_top_k
        self._filters = filters
        super().__init__()

    @staticmethod
    def _default_vector_store(extractor: Optional[BGEM3EmbeddingExtractor]):
        extractor = extractor or BGEM3EmbeddingExtractor()
        qdrant = QdrantManager()
        return QdrantVectorStore(
            collection_name=settings.qdrant_collection_name,
            client=qdrant.client,
            enable_hybrid=True,
            sparse_query_fn=sparse_bge_m3_encoder(extractor),
        )

    def _retrieve(self, query_bundle) -> Sequence[NodeWithScore]:
        query_str = query_bundle.query_str
        query = VectorStoreQuery(
            query_str=query_str,
            similarity_top_k=self._similarity_top_k,
            mode=VectorStoreQueryMode.SPARSE,
            filters=self._filters,
        )
        result: VectorStoreQueryResult = self._vector_store.query(query)
        return self._to_nodes(result)

    @staticmethod
    def _to_nodes(result: VectorStoreQueryResult) -> List[NodeWithScore]:
        nodes: List[NodeWithScore] = []
        for node, score in zip(result.nodes, result.similarities):
            nodes.append(NodeWithScore(node=node, score=score))
        return nodes


class LlamaIndexRRFRetriever(BaseRetriever):
    """LlamaIndex retriever exposing database-level RRF hybrid search.

    Every ``retrieve()`` call sends a single Qdrant ``query_points`` request
    with two parallel prefetches (dense + sparse) fused server-side with
    Reciprocal Rank Fusion.  The returned nodes are the fused top-k chunks.
    """

    def __init__(
        self,
        db_manager: Optional[QdrantManager] = None,
        extractor: Optional[BGEM3EmbeddingExtractor] = None,
        similarity_top_k: int = 25,
        dense_candidates: Optional[int] = None,
        sparse_candidates: Optional[int] = None,
        filters: Optional[MetadataFilters] = None,
    ):
        self._db_manager = db_manager or QdrantManager()
        self._extractor = extractor or BGEM3EmbeddingExtractor()
        self._similarity_top_k = similarity_top_k
        self._dense_candidates = dense_candidates
        self._sparse_candidates = sparse_candidates
        self._filters = filters
        super().__init__()

    def _retrieve(self, query_bundle) -> Sequence[NodeWithScore]:
        query_str = query_bundle.query_str
        dense_vec, sparse = self._extractor.embed_query(query_str)
        results = self._db_manager.search_hybrid_rrf(
            query_vector=dense_vec,
            sparse_indices=sparse.indices,
            sparse_values=sparse.values,
            limit=self._similarity_top_k,
            dense_limit=self._dense_candidates,
            sparse_limit=self._sparse_candidates,
        )
        nodes: List[NodeWithScore] = []
        for r in results:
            node = TextNode(
                id_=r.chunk_id,
                text=r.text,
                metadata=dict(r.payload),
                score=r.score,
            )
            nodes.append(NodeWithScore(node=node, score=r.score))
        return nodes