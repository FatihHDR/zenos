"""End-to-end Phase 3 test: in-memory Qdrant + fake extractor/reranker and a fake Claude client."""

from unittest.mock import MagicMock

from db.qdrant import QdrantManager
from embeddings.bge_m3 import SparseVectorData
from generation.generator import GroundedGenerator
from generation.pipeline import GroundedQAPipeline
from models import DocumentChunk, DocumentMetadata
from reranking.reranker import BaseReranker


class FakeExtractor:
    """Stand-in for BGEM3EmbeddingExtractor with fixed 3-dim vectors."""

    def embed_query(self, query: str):
        return [0.9, 0.1, 0.1], SparseVectorData(indices=[1, 3], values=[0.9, 0.7])


class FixedReranker(BaseReranker):
    """Deterministic reranker that always puts ``d0_p1_c0`` first."""

    def rerank(self, query, results, top_n=5):
        scores = [1.0 if r.chunk_id == "d0_p1_c0" else 0.1 for r in results]
        return self._rank(results, scores, top_n)


def _fake_client(text):
    client = MagicMock()
    client.messages.create.return_value = MagicMock(content=[MagicMock(text=text)])
    return client


def _seed_collection():
    manager = QdrantManager(use_memory=True)
    collection = "test_qa"
    manager.init_collection(collection_name=collection, dense_dim=3, recreate=True)

    def make(chunk_id, text, dense, sparse_idx, sparse_val):
        doc_id = chunk_id.split("_")[0]
        return DocumentChunk(
            chunk_id=chunk_id,
            text=text,
            metadata=DocumentMetadata(
                doc_id=doc_id,
                source_name=f"{doc_id}.txt",
                page_number=1,
                chunk_index=0,
                total_chunks=1,
                token_count=8,
            ),
            dense_vector=dense,
            sparse_indices=sparse_idx,
            sparse_values=sparse_val,
        )

    manager.upsert_chunks(
        [
            make(
                "d0_p1_c0",
                "UU Perlindungan Data Pribadi mengatur asas perlindungan data.",
                [0.9, 0.1, 0.1],
                [1, 3],
                [0.9, 0.7],
            ),
            make(
                "d1_p1_c0",
                "Virtual memory page fault handling in the kernel.",
                [0.1, 0.9, 0.1],
                [2, 4],
                [0.8, 0.6],
            ),
        ],
        collection_name=collection,
    )

    # Pin the collection name so the pipeline's default search hits our seed data.
    original = manager.search_hybrid_rrf

    def patched(*args, **kwargs):
        kwargs["collection_name"] = collection
        return original(*args, **kwargs)

    manager.search_hybrid_rrf = patched  # type: ignore[method-assign]
    return manager


def _build_pipeline(top_n=1):
    client = _fake_client(
        "Asas perlindungan data wajib dipatuhi [Source: d0.txt, Pg 1]."
    )
    return GroundedQAPipeline(
        db_manager=_seed_collection(),
        extractor=FakeExtractor(),
        reranker=FixedReranker(),
        generator=GroundedGenerator(client=client),
        candidates=5,
        top_n=top_n,
    )


def test_answer_end_to_end_returns_validated_citation():
    answer = _build_pipeline(top_n=1).answer("asas perlindungan data pribadi")

    assert answer.grounded is True
    assert answer.refused is False
    assert answer.context_chunk_ids == ["d0_p1_c0"]
    assert len(answer.citations) == 1
    assert answer.citations[0].chunk_id == "d0_p1_c0"
    assert answer.citations[0].source_name == "d0.txt"
    assert answer.citations[0].page_number == 1


def test_answer_with_context_returns_reranked_chunks():
    reranked, answer = _build_pipeline(top_n=2).answer_with_context("asas perlindungan data")

    assert len(reranked) == 2
    assert reranked[0].chunk_id == "d0_p1_c0"
    assert reranked[0].original_score is not None
    assert answer.grounded is True
