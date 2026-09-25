"""Dual dense and sparse embedding extractor supporting BAAI/bge-m3 via FlagEmbedding and FastEmbed."""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from pydantic import BaseModel

from config import settings
from models import DocumentChunk

logger = logging.getLogger(__name__)


class SparseVectorData(BaseModel):
    """Container for sparse vector representation."""

    indices: List[int]
    values: List[float]


class BGEM3EmbeddingExtractor:
    """Extracts dual dense and sparse representations using BAAI/bge-m3 or FastEmbed."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        dense_model_name: Optional[str] = None,
        sparse_model_name: Optional[str] = None,
        use_fastembed: bool = False,
        cache_dir: Optional[str] = None,
        device: Optional[str] = None,
    ):
        self.model_name = model_name or settings.dense_model_name
        self.dense_model_name = dense_model_name or settings.dense_model_name
        self.sparse_model_name = sparse_model_name or settings.sparse_model_name
        self.use_fastembed = use_fastembed
        self.cache_dir = str(cache_dir) if cache_dir else (str(settings.cache_dir) if settings.cache_dir else None)
        self.device = device

        self._flag_model = None
        self._fastembed_dense = None
        self._fastembed_sparse = None

    def _init_flag_model(self):
        """Initialize FlagEmbedding BGEM3FlagModel for single-pass dual embeddings."""
        if self._flag_model is None:
            try:
                from FlagEmbedding import BGEM3FlagModel

                logger.info(f"Loading BGEM3FlagModel ({self.model_name})...")
                self._flag_model = BGEM3FlagModel(
                    self.model_name,
                    use_fp16=False,
                    cache_dir=self.cache_dir,
                    device=self.device,
                )
            except Exception as e:
                logger.warning(f"Could not load FlagEmbedding BGEM3FlagModel: {e}. Falling back to FastEmbed.")
                self.use_fastembed = True

    def _init_fastembed_dense(self):
        if self._fastembed_dense is None:
            from fastembed import TextEmbedding

            try:
                self._fastembed_dense = TextEmbedding(
                    model_name=self.dense_model_name,
                    cache_dir=self.cache_dir,
                )
            except Exception:
                # Fallback to BGE large/base onnx
                self._fastembed_dense = TextEmbedding(
                    model_name="BAAI/bge-large-en-v1.5",
                    cache_dir=self.cache_dir,
                )

    def _init_fastembed_sparse(self):
        if self._fastembed_sparse is None:
            from fastembed import SparseTextEmbedding

            try:
                self._fastembed_sparse = SparseTextEmbedding(
                    model_name=self.sparse_model_name,
                    cache_dir=self.cache_dir,
                )
            except Exception:
                self._fastembed_sparse = SparseTextEmbedding(
                    model_name="Qdrant/bm25",
                    cache_dir=self.cache_dir,
                )

    def embed_texts(
        self, texts: List[str], batch_size: int = 16
    ) -> Tuple[List[List[float]], List[SparseVectorData]]:
        """Compute both dense and sparse representations for a list of texts."""
        if not texts:
            return [], []

        if not self.use_fastembed:
            self._init_flag_model()

        if self._flag_model is not None and not self.use_fastembed:
            # Single-pass dual inference with BAAI/bge-m3
            output = self._flag_model.encode(
                texts,
                batch_size=batch_size,
                max_length=512,
                return_dense=True,
                return_sparse=True,
                return_colbert_vecs=False,
            )

            dense_vecs = [v.tolist() for v in output["dense_vecs"]]
            sparse_vecs: List[SparseVectorData] = []
            for item in output["lexical_weights"]:
                # item is dict of {token_id_str: weight}
                indices = [int(k) for k in item.keys()]
                values = [float(v) for v in item.values()]
                sparse_vecs.append(SparseVectorData(indices=indices, values=values))

            return dense_vecs, sparse_vecs
        else:
            # FastEmbed fallback
            self._init_fastembed_dense()
            self._init_fastembed_sparse()

            dense_iter = self._fastembed_dense.embed(texts, batch_size=batch_size)
            dense_vecs = [
                emb.tolist() if isinstance(emb, np.ndarray) else list(emb)
                for emb in dense_iter
            ]

            sparse_iter = self._fastembed_sparse.embed(texts, batch_size=batch_size)
            sparse_vecs: List[SparseVectorData] = []
            for sparse_emb in sparse_iter:
                indices = (
                    sparse_emb.indices.tolist()
                    if hasattr(sparse_emb.indices, "tolist")
                    else list(sparse_emb.indices)
                )
                values = (
                    sparse_emb.values.tolist()
                    if hasattr(sparse_emb.values, "tolist")
                    else list(sparse_emb.values)
                )
                sparse_vecs.append(SparseVectorData(indices=indices, values=values))

            return dense_vecs, sparse_vecs

    def embed_chunks(
        self, chunks: List[DocumentChunk], batch_size: int = 16
    ) -> List[DocumentChunk]:
        """Generate dual dense and sparse embeddings and attach to DocumentChunks."""
        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]
        dense_vectors, sparse_vectors = self.embed_texts(texts, batch_size=batch_size)

        for chunk, dense, sparse in zip(chunks, dense_vectors, sparse_vectors):
            chunk.dense_vector = dense
            chunk.sparse_indices = sparse.indices
            chunk.sparse_values = sparse.values

        return chunks

    def embed_query(self, query: str) -> Tuple[List[float], SparseVectorData]:
        """Compute dual dense and sparse vectors for a search query."""
        dense_vecs, sparse_vecs = self.embed_texts([query], batch_size=1)
        return dense_vecs[0], sparse_vecs[0]
