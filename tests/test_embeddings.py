"""Tests for dual dense and sparse embedding extractor."""

import pytest
from embeddings.bge_m3 import BGEM3EmbeddingExtractor
from models import DocumentChunk, DocumentMetadata


def test_embedding_extractor_fastembed_fallback():
    extractor = BGEM3EmbeddingExtractor(use_fastembed=True)

    texts = [
        "Operating systems manage memory with page tables and translation lookaside buffers.",
        "UU Perlindungan Data Pribadi mengatur hak dan kewajiban pengendali data pribadi.",
    ]

    dense_vecs, sparse_vecs = extractor.embed_texts(texts)

    assert len(dense_vecs) == 2
    assert len(sparse_vecs) == 2

    # Verify dense vector dimension
    assert len(dense_vecs[0]) > 0

    # Verify sparse vector has valid token indices and values
    assert len(sparse_vecs[0].indices) > 0
    assert len(sparse_vecs[0].values) == len(sparse_vecs[0].indices)


def test_embed_chunks():
    extractor = BGEM3EmbeddingExtractor(use_fastembed=True)
    chunks = [
        DocumentChunk(
            chunk_id="doc1_p1_c0",
            text="Virtual memory allows programs to address more memory than physical RAM.",
            metadata=DocumentMetadata(
                doc_id="doc1",
                source_name="os.txt",
                page_number=1,
                chunk_index=0,
                total_chunks=1,
                token_count=12,
            ),
        )
    ]

    embedded_chunks = extractor.embed_chunks(chunks)
    assert len(embedded_chunks) == 1
    assert embedded_chunks[0].dense_vector is not None
    assert embedded_chunks[0].sparse_indices is not None
    assert embedded_chunks[0].sparse_values is not None
