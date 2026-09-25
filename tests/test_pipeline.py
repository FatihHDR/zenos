"""End-to-end integration tests for IngestionPipeline with in-memory Qdrant."""

from pathlib import Path
from db.qdrant import QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor
from ingestion.chunker import TokenChunker
from ingestion.parser import DocumentParser
from ingestion.pipeline import IngestionPipeline


def test_end_to_end_ingestion_pipeline():
    # Setup in-memory Qdrant
    db_manager = QdrantManager(use_memory=True)
    extractor = BGEM3EmbeddingExtractor(use_fastembed=True)
    chunker = TokenChunker(chunk_size=512, chunk_overlap=100)
    parser = DocumentParser()

    pipeline = IngestionPipeline(
        db_manager=db_manager,
        embedding_extractor=extractor,
        chunker=chunker,
        parser=parser,
    )

    # Initialize collection
    pipeline.prepare_db(recreate=True)

    # Test ingesting markdown document
    md_path = Path("data/sample_docs/legal_uu_pdp_2022.md")
    result = pipeline.ingest_file(md_path)
    assert result.success is True
    assert result.num_chunks >= 1
    assert result.source_name == "legal_uu_pdp_2022.md"

    # Test ingesting PDF document
    pdf_path = Path("data/sample_docs/os_paging_overview.pdf")
    pdf_result = pipeline.ingest_file(pdf_path)
    assert pdf_result.success is True
    assert pdf_result.num_chunks == 2
    assert pdf_result.source_name == "os_paging_overview.pdf"

    # Verify total points in Qdrant
    total_points = db_manager.count_points()
    assert total_points == result.num_chunks + pdf_result.num_chunks
