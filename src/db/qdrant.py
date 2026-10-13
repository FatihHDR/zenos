"""Qdrant client and collection manager supporting dual dense and sparse vector indexing."""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Fusion, FusionQuery, Prefetch, QueryRequest

from config import settings
from models import DocumentChunk

logger = logging.getLogger(__name__)


class HybridSearchResult:
    """A single fused result from a hybrid search."""

    __slots__ = ("chunk_id", "text", "score", "payload", "dense_score", "sparse_score")

    def __init__(self, chunk_id: str, text: str, score: float, payload: Dict[str, Any],
                 dense_score: Optional[float] = None, sparse_score: Optional[float] = None):
        self.chunk_id = chunk_id
        self.text = text
        self.score = score
        self.payload = payload
        self.dense_score = dense_score
        self.sparse_score = sparse_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "score": self.score,
            "dense_score": self.dense_score,
            "sparse_score": self.sparse_score,
            "metadata": self.payload,
        }

    def __repr__(self) -> str:
        return f"HybridSearchResult(chunk_id={self.chunk_id!r}, score={self.score:.4f})"


class QdrantManager:
    """Manages Qdrant client connection, dual-indexed collection creation, and point ingestion."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        grpc_port: Optional[int] = None,
        api_key: Optional[str] = None,
        use_memory: Optional[bool] = None,
        local_path: Optional[str] = None,
    ):
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.grpc_port = grpc_port or settings.qdrant_grpc_port
        self.api_key = api_key or settings.qdrant_api_key
        self.use_memory = use_memory if use_memory is not None else settings.qdrant_use_local_memory
        self.local_path = local_path or settings.qdrant_local_path

        self.client = self._init_client()

    def _init_client(self) -> QdrantClient:
        """Initialize Qdrant client based on configuration."""
        if self.use_memory:
            return QdrantClient(location=":memory:")
        elif self.local_path:
            return QdrantClient(path=self.local_path)
        else:
            return QdrantClient(
                host=self.host,
                port=self.port,
                grpc_port=self.grpc_port,
                api_key=self.api_key,
                prefer_grpc=False,
                timeout=30.0,
            )

    def init_collection(
        self,
        collection_name: Optional[str] = None,
        dense_vector_name: Optional[str] = None,
        sparse_vector_name: Optional[str] = None,
        dense_dim: Optional[int] = None,
        recreate: bool = False,
    ) -> bool:
        """Ensure collection is configured with both dense and sparse vector spaces in a single collection."""
        name = collection_name or settings.qdrant_collection_name
        dense_name = dense_vector_name or settings.dense_vector_name
        sparse_name = sparse_vector_name or settings.sparse_vector_name
        dim = dense_dim or settings.embedding_dimension

        collections = self.client.get_collections().collections
        exists = any(c.name == name for c in collections)

        if exists:
            if recreate:
                self.client.delete_collection(collection_name=name)
            else:
                return True

        # Configure dual vector schema: dense (Cosine) + sparse (BM25/BGE-M3)
        vectors_config = {
            dense_name: models.VectorParams(
                size=dim,
                distance=models.Distance.COSINE,
            )
        }

        sparse_vectors_config = {
            sparse_name: models.SparseVectorParams(
                index=models.SparseIndexParams(
                    on_disk=False,
                )
            )
        }

        self.client.create_collection(
            collection_name=name,
            vectors_config=vectors_config,
            sparse_vectors_config=sparse_vectors_config,
        )

        # Setup payload indexes for high performance filtering and metadata retrieval
        self._create_payload_indexes(name)
        return True

    def _create_payload_indexes(self, collection_name: str) -> None:
        """Create payload indexes on key metadata fields."""
        index_fields = [
            ("doc_id", models.PayloadSchemaType.KEYWORD),
            ("source_name", models.PayloadSchemaType.KEYWORD),
            ("page_number", models.PayloadSchemaType.INTEGER),
            ("chunk_index", models.PayloadSchemaType.INTEGER),
        ]

        for field_name, schema_type in index_fields:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=schema_type,
                )
            except Exception:
                pass

    def upsert_chunks(
        self,
        chunks: List[DocumentChunk],
        collection_name: Optional[str] = None,
        dense_vector_name: Optional[str] = None,
        sparse_vector_name: Optional[str] = None,
        batch_size: int = 64,
    ) -> int:
        """Upsert document chunks with dual vectors and metadata payload into Qdrant."""
        if not chunks:
            return 0

        name = collection_name or settings.qdrant_collection_name
        dense_name = dense_vector_name or settings.dense_vector_name
        sparse_name = sparse_vector_name or settings.sparse_vector_name

        points: List[models.PointStruct] = []
        for chunk in chunks:
            if chunk.dense_vector is None or chunk.sparse_indices is None or chunk.sparse_values is None:
                raise ValueError(
                    f"Chunk {chunk.chunk_id} missing dense or sparse embedding vectors."
                )

            # Generate deterministic UUID for idempotent upserts
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))

            vector_dict = {
                dense_name: chunk.dense_vector,
                sparse_name: models.SparseVector(
                    indices=chunk.sparse_indices,
                    values=chunk.sparse_values,
                ),
            }

            payload = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "doc_id": chunk.metadata.doc_id,
                "source_name": chunk.metadata.source_name,
                "page_number": chunk.metadata.page_number,
                "chunk_index": chunk.metadata.chunk_index,
                "total_chunks": chunk.metadata.total_chunks,
                "token_count": chunk.metadata.token_count,
                "created_at": chunk.metadata.created_at,
                "extra": chunk.metadata.extra,
            }

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector_dict,
                    payload=payload,
                )
            )

        # Upsert in batches
        total_upserted = 0
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=name,
                points=batch,
                wait=True,
            )
            total_upserted += len(batch)

        return total_upserted

    def search_dense(
        self,
        query_vector: List[float],
        limit: int = 25,
        collection_name: Optional[str] = None,
        vector_name: Optional[str] = None,
        score_threshold: Optional[float] = None,
    ) -> List[HybridSearchResult]:
        """Run a pure dense (semantic) search against the collection."""
        name = collection_name or settings.qdrant_collection_name
        vec_name = vector_name or settings.dense_vector_name
        response = self.client.query_points(
            collection_name=name,
            query=query_vector,
            using=vec_name,
            limit=limit,
            with_payload=True,
            score_threshold=score_threshold,
        )
        return [
            HybridSearchResult(
                chunk_id=p.payload.get("chunk_id", str(p.id)),
                text=p.payload.get("text", ""),
                score=float(p.score),
                payload=dict(p.payload),
                dense_score=float(p.score),
            )
            for p in response.points
        ]

    def search_sparse(
        self,
        sparse_indices: List[int],
        sparse_values: List[float],
        limit: int = 25,
        collection_name: Optional[str] = None,
        vector_name: Optional[str] = None,
        score_threshold: Optional[float] = None,
    ) -> List[HybridSearchResult]:
        """Run a pure sparse (lexical / BM25) search against the collection."""
        name = collection_name or settings.qdrant_collection_name
        vec_name = vector_name or settings.sparse_vector_name
        sparse_query = models.SparseVector(indices=sparse_indices, values=sparse_values)
        response = self.client.query_points(
            collection_name=name,
            query=sparse_query,
            using=vec_name,
            limit=limit,
            with_payload=True,
            score_threshold=score_threshold,
        )
        return [
            HybridSearchResult(
                chunk_id=p.payload.get("chunk_id", str(p.id)),
                text=p.payload.get("text", ""),
                score=float(p.score),
                payload=dict(p.payload),
                sparse_score=float(p.score),
            )
            for p in response.points
        ]

    def search_hybrid_rrf(
        self,
        query_vector: List[float],
        sparse_indices: List[int],
        sparse_values: List[float],
        limit: int = 25,
        dense_limit: Optional[int] = None,
        sparse_limit: Optional[int] = None,
        collection_name: Optional[str] = None,
        dense_vector_name: Optional[str] = None,
        sparse_vector_name: Optional[str] = None,
        fusion: Optional[Fusion] = None,
        score_threshold: Optional[float] = None,
        with_vectors: bool = False,
    ) -> List[HybridSearchResult]:
        """Run parallel dense and sparse searches and fuse the rankings at the database level.

        This mirrors how the PRD (Phase 2) wants the search to behave: both the
        semantic (dense) and the exact-keyword (sparse) search are executed by
        Qdrant as parallel prefetches, and the final ranking is produced by
        Qdrant's own Reciprocal Rank Fusion (``Fusion.RRF``) — i.e. the fusion
        happens *at the database level*, before results ever reach the client.

        Args:
            query_vector: Dense query embedding (BGE-M3, 1024 dims).
            sparse_indices: Sparse token indices of the query (BGE-M3 lexical).
            sparse_values: Sparse token weights of the query.
            limit: Number of fused results to return.
            dense_limit: Candidate count per dense prefetch (defaults to ``limit``,
                but a larger candidate pool improves RRF ranking quality).
            sparse_limit: Candidate count per sparse prefetch (defaults to ``limit``).
            fusion: Fusion strategy, defaults to ``Fusion.RRF``.
            score_threshold: Optional minimum fused score.
            with_vectors: Return stored vectors alongside payloads.

        Returns:
            A list of :class:`HybridSearchResult` ordered by fused RRF score
            descending.
        """
        name = collection_name or settings.qdrant_collection_name
        dense_name = dense_vector_name or settings.dense_vector_name
        sparse_name = sparse_vector_name or settings.sparse_vector_name
        fusion = fusion or Fusion.RRF
        dense_top = dense_limit or limit
        sparse_top = sparse_limit or limit

        prefetch = [
            Prefetch(
                query=query_vector,
                using=dense_name,
                limit=dense_top,
            ),
            Prefetch(
                query=models.SparseVector(indices=sparse_indices, values=sparse_values),
                using=sparse_name,
                limit=sparse_top,
            ),
        ]

        response = self.client.query_points(
            collection_name=name,
            prefetch=prefetch,
            query=FusionQuery(fusion=fusion),
            limit=limit,
            with_payload=True,
            with_vectors=with_vectors,
            score_threshold=score_threshold,
        )

        results: List[HybridSearchResult] = []
        for p in response.points:
            payload = dict(p.payload) if p.payload else {}
            # For prefetch+fused queries each point also carries the per-vector
            # scores of its *best* prefetch hit, which is useful diagnostics.
            dense_score = None
            sparse_score = None
            if isinstance(p.vector, dict):
                dense_vec = p.vector.get(dense_name)
                sparse_vec = p.vector.get(sparse_name)
                if isinstance(dense_vec, list) and dense_vec:
                    dense_score = float(dense_vec[0]) if isinstance(dense_vec[0], (int, float)) else None
                if isinstance(sparse_vec, list) and sparse_vec:
                    sparse_score = float(sparse_vec[0]) if isinstance(sparse_vec[0], (int, float)) else None

            results.append(
                HybridSearchResult(
                    chunk_id=payload.get("chunk_id", str(p.id)),
                    text=payload.get("text", ""),
                    score=float(p.score),
                    payload=payload,
                    dense_score=dense_score,
                    sparse_score=sparse_score,
                )
            )
        return results

    def count_points(self, collection_name: Optional[str] = None) -> int:
        """Return total count of points in the collection."""
        name = collection_name or settings.qdrant_collection_name
        try:
            info = self.client.get_collection(collection_name=name)
            return info.points_count or 0
        except Exception:
            return 0

    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get collection status and configuration details."""
        name = collection_name or settings.qdrant_collection_name
        info = self.client.get_collection(collection_name=name)
        return {
            "status": str(info.status),
            "points_count": info.points_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "vectors_config": str(info.config.params.vectors),
            "sparse_vectors_config": str(info.config.params.sparse_vectors),
        }
