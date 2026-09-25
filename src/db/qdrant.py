"""Qdrant client and collection manager supporting dual dense and sparse vector indexing."""

import uuid
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models

from config import settings
from models import DocumentChunk


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
