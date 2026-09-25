"""Tests for QdrantManager and dual vector schema configuration."""

from db.qdrant import QdrantManager
from models import DocumentChunk, DocumentMetadata


def test_qdrant_manager_in_memory():
    manager = QdrantManager(use_memory=True)
    collection_name = "test_collection"

    # Initialize collection
    success = manager.init_collection(collection_name=collection_name, recreate=True)
    assert success is True

    # Check info
    info = manager.get_collection_info(collection_name=collection_name)
    assert info["points_count"] == 0

    # Upsert chunk
    chunk = DocumentChunk(
        chunk_id="test_doc_p1_c0",
        text="This is a test chunk for Qdrant dual index verification.",
        metadata=DocumentMetadata(
            doc_id="test_doc",
            source_name="test.txt",
            page_number=1,
            chunk_index=0,
            total_chunks=1,
            token_count=10,
        ),
        dense_vector=[0.1] * 1024,
        sparse_indices=[1, 42, 108],
        sparse_values=[0.5, 0.8, 0.3],
    )

    upserted = manager.upsert_chunks([chunk], collection_name=collection_name)
    assert upserted == 1

    count = manager.count_points(collection_name=collection_name)
    assert count == 1
