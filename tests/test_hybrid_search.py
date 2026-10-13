"""Integration tests for database-level hybrid (dense + sparse) search with RRF fusion.

These tests exercise the full Phase 2 path against an in-memory Qdrant,
including parallel prefetches and server-side Reciprocal Rank Fusion via
``FusionQuery(fusion=Fusion.RRF)``.
"""

from qdrant_client.http.models import Fusion

from db.qdrant import HybridSearchResult, QdrantManager
from models import DocumentChunk, DocumentMetadata


def _make_chunk(chunk_id: str, text: str, dense: list, sparse_idx: list, sparse_val: list):
    return DocumentChunk(
        chunk_id=chunk_id,
        text=text,
        metadata=DocumentMetadata(
            doc_id=chunk_id.split("_")[0],
            source_name=f"{chunk_id}.txt",
            page_number=1,
            chunk_index=0,
            total_chunks=1,
            token_count=len(text.split()),
        ),
        dense_vector=dense,
        sparse_indices=sparse_idx,
        sparse_values=sparse_val,
    )


def _seed_hybrid_collection() -> tuple:
    """Seed an in-memory Qdrant collection with a few dual-vector chunks and
    return ``(manager, collection_name)``."""
    manager = QdrantManager(use_memory=True)
    collection_name = "test_hybrid"

    # Seed with 3-dim dense vectors to stay small and fast.
    assert manager.init_collection(
        collection_name=collection_name, dense_dim=3, recreate=True
    )
    chunks = [
        _make_chunk(
            "d0_p1_c0",
            "UU Perlindungan Data Pribadi mengatur asas dan kewajiban pengendali data.",
            [0.9, 0.1, 0.1], [1, 3, 5], [0.9, 0.7, 0.4],
        ),
        _make_chunk(
            "d1_p1_c0",
            "Kernel page fault handling in virtual memory systems.",
            [0.1, 0.9, 0.1], [2, 4, 6], [0.8, 0.6, 0.3],
        ),
        _make_chunk(
            "d2_p1_c0",
            "A completely unrelated chunk about recipes and cooking.",
            [0.1, 0.1, 0.9], [7, 8, 9], [0.5, 0.5, 0.5],
        ),
    ]
    upserted = manager.upsert_chunks(chunks, collection_name=collection_name)
    assert upserted == 3
    return manager, collection_name


def test_search_dense_returns_ordered_results():
    manager, coll = _seed_hybrid_collection()
    # Query vector close to c0's dense vector
    results = manager.search_dense(
        query_vector=[0.85, 0.1, 0.1], limit=3, collection_name=coll
    )
    assert len(results) == 3
    assert all(isinstance(r, HybridSearchResult) for r in results)
    # First result should be the semantically most similar chunk
    assert results[0].chunk_id == "d0_p1_c0"
    assert results[0].dense_score is not None
    assert results[0].text.startswith("UU Perlindungan")


def test_search_sparse_returns_lexical_results():
    manager, coll = _seed_hybrid_collection()
    # Query sparse vector with the same tokens as c0's sparse layout
    results = manager.search_sparse(
        sparse_indices=[1, 3], sparse_values=[0.9, 0.7], limit=3, collection_name=coll
    )
    assert len(results) >= 1
    # c0 has tokens 1 and 3 with weights 0.9/0.7 -> should be top
    assert results[0].chunk_id == "d0_p1_c0"
    assert results[0].sparse_score is not None


def test_search_hybrid_rrf_fuses_both_retrievers():
    manager, coll = _seed_hybrid_collection()
    results = manager.search_hybrid_rrf(
        query_vector=[0.85, 0.1, 0.1],
        sparse_indices=[1, 3],
        sparse_values=[0.9, 0.7],
        limit=3,
        collection_name=coll,
    )
    assert len(results) >= 2
    # Fused RRF should rank c0 first (it is best in both dense and sparse)
    assert results[0].chunk_id == "d0_p1_c0"
    # Score should be a fused RRF value (0 < score <= 1)
    assert 0.0 < results[0].score <= 1.0


def test_search_hybrid_rrf_fusion_enum():
    manager, coll = _seed_hybrid_collection()
    # Explicitly request RRF fusion
    results = manager.search_hybrid_rrf(
        query_vector=[0.1, 0.9, 0.1],
        sparse_indices=[2, 4],
        sparse_values=[0.8, 0.6],
        limit=3,
        collection_name=coll,
        fusion=Fusion.RRF,
    )
    # c1 is the best match for this query
    assert results[0].chunk_id == "d1_p1_c0"


def test_search_hybrid_rrf_candidate_pool():
    manager, coll = _seed_hybrid_collection()
    # Larger candidate pools should still return limit results
    results = manager.search_hybrid_rrf(
        query_vector=[0.85, 0.1, 0.1],
        sparse_indices=[1, 3],
        sparse_values=[0.9, 0.7],
        limit=2,
        dense_limit=5,
        sparse_limit=5,
        collection_name=coll,
    )
    assert len(results) == 2
    assert results[0].chunk_id == "d0_p1_c0"