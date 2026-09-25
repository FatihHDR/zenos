"""Tests for token chunker."""

import pytest
from ingestion.chunker import TokenChunker
from models import DocumentPage, RawDocument


def test_chunker_small_text():
    chunker = TokenChunker(chunk_size=512, chunk_overlap=100)
    text = "This is a brief text about operating system kernel architecture."
    chunks = chunker.chunk_text(
        text=text,
        doc_id="doc_1",
        source_name="doc.txt",
        page_number=1,
    )
    assert len(chunks) == 1
    assert chunks[0].chunk_id == "doc_1_p1_c0"
    assert chunks[0].metadata.doc_id == "doc_1"
    assert chunks[0].metadata.page_number == 1
    assert chunks[0].metadata.token_count > 0
    assert chunks[0].metadata.token_count <= 512


def test_chunker_long_text_overlap():
    chunker = TokenChunker(chunk_size=100, chunk_overlap=20)
    # Generate long text of 250 words
    words = ["word" + str(i) for i in range(250)]
    long_text = " ".join(words)

    chunks = chunker.chunk_text(
        text=long_text,
        doc_id="doc_long",
        source_name="long.txt",
        page_number=1,
    )

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.metadata.token_count <= 100

    # Ensure step between chunks corresponds to chunk_size - overlap
    assert chunks[0].metadata.chunk_index == 0
    assert chunks[1].metadata.chunk_index == 1


def test_chunk_raw_document():
    chunker = TokenChunker(chunk_size=512, chunk_overlap=100)
    raw_doc = RawDocument(
        doc_id="doc_pages",
        source_name="doc_pages.pdf",
        file_type=".pdf",
        pages=[
            DocumentPage(page_number=1, text="Page one content about memory management."),
            DocumentPage(page_number=2, text="Page two content about process scheduling."),
        ],
    )
    chunks = chunker.chunk_document(raw_doc)
    assert len(chunks) == 2
    assert chunks[0].metadata.page_number == 1
    assert chunks[1].metadata.page_number == 2
    assert chunks[0].metadata.total_chunks == 2
    assert chunks[1].metadata.total_chunks == 2
