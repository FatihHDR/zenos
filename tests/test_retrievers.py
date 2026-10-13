"""Smoke tests for the LlamaIndex parallel retriever modules (Phase 2).

These tests avoid loading the full BGE-M3 model by injecting a lightweight
fake extractor and an in-memory Qdrant, so they run fast and offline.
"""

from unittest.mock import MagicMock

from llama_index.core.schema import TextNode

from db.qdrant import HybridSearchResult, QdrantManager
from models import DocumentChunk, DocumentMetadata
from embeddings.bge_m3 import SparseVectorData
from retrieval.llama_retrievers import (
    DenseRetriever,
    LlamaIndexRRFRetriever,
    SparseRetriever,
)


class FakeExtractor:
    """Minimal stand-in for BGEM3EmbeddingExtractor with fixed vectors."""

    def __init__(self):
        self.dense = [0.9, 0.1, 0.1]
        self.sparse = SparseVectorData(indices=[1, 3], values=[0.9, 0.7])

    def embed_query(self, query: str):
        return self.dense, self.sparse


def _seed_collection() -> tuple:
    manager = QdrantManager(use_memory=True)
    coll = "test_retriever"
    # In-memory Qdrant needs matching dims; use 3-dim dense vectors.
    manager.init_collection(collection_name=coll, dense_dim=3, recreate=True)
    chunks = [
        DocumentChunk(
            chunk_id="d0_p1_c0",
            text="UU Perlindungan Data Pribadi mengatur asas perlindungan data.",
            metadata=DocumentMetadata(
                doc_id="d0", source_name="d0.txt", page_number=1,
                chunk_index=0, total_chunks=1, token_count=8,
            ),
            dense_vector=[0.9, 0.1, 0.1],
            sparse_indices=[1, 3],
            sparse_values=[0.9, 0.7],
        ),
        DocumentChunk(
            chunk_id="d1_p1_c0",
            text="Virtual memory page fault handling in the kernel.",
            metadata=DocumentMetadata(
                doc_id="d1", source_name="d1.txt", page_number=1,
                chunk_index=0, total_chunks=1, token_count=7,
            ),
            dense_vector=[0.1, 0.9, 0.1],
            sparse_indices=[2, 4],
            sparse_values=[0.8, 0.6],
        ),
    ]
    manager.upsert_chunks(chunks, collection_name=coll)
    return manager, coll


def test_dense_retriever_returns_nodes():
    manager, coll = _seed_collection()
    store = MagicMock()
    store.query.return_value = MagicMock(
        nodes=[TextNode(id_="d0_p1_c0", text="UU Perlindungan Data Pribadi mengatur asas perlindungan data.")],
        similarities=[0.95],
    )
    retriever = DenseRetriever(vector_store=store, extractor=FakeExtractor(), similarity_top_k=25)
    nodes = retriever.retrieve("asas perlindungan data pribadi")
    assert len(nodes) == 1
    assert nodes[0].score == 0.95


def test_sparse_retriever_returns_nodes():
    manager, coll = _seed_collection()
    store = MagicMock()
    store.query.return_value = MagicMock(
        nodes=[TextNode(id_="d0_p1_c0", text="UU Perlindungan Data Pribadi mengatur asas perlindungan data.")],
        similarities=[1.2],
    )
    retriever = SparseRetriever(vector_store=store, extractor=FakeExtractor(), similarity_top_k=25)
    nodes = retriever.retrieve("perlindungan data pribadi")
    assert len(nodes) == 1
    assert nodes[0].node.id_ == "d0_p1_c0"


def test_llama_rrf_retriever_integration():
    """Fully end-to-end: fake extractor + real in-memory Qdrant with RRF fusion."""
    manager, coll = _seed_collection()
    # Point the retriever at the seeded in-memory collection
    retriever = LlamaIndexRRFRetriever(
        db_manager=manager,
        extractor=FakeExtractor(),
        similarity_top_k=25,
        dense_candidates=10,
        sparse_candidates=10,
    )
    # Monkey-patch the collection name in place: manager defaults use settings,
    # so pass an explicit collection override by wrapping.
    original_search = manager.search_hybrid_rrf

    import functools

    def patched_search(*args, **kwargs):
        kwargs["collection_name"] = coll
        return original_search(*args, **kwargs)

    manager.search_hybrid_rrf = patched_search  # type: ignore[method-assign]
    try:
        nodes = retriever.retrieve("perlindungan data pribadi")
    finally:
        manager.search_hybrid_rrf = original_search  # type: ignore[method-assign]
    assert len(nodes) >= 1
    assert nodes[0].node.id_ == "d0_p1_c0"