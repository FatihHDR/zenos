"""Tests for the configurable retrieval mode and the reranker toggle (PRD Section 3).

Offline: every dependency is faked, so no model is loaded and no database is needed.
"""

import pytest

from db.qdrant import HybridSearchResult
from embeddings.bge_m3 import SparseVectorData
from generation.pipeline import GroundedQAPipeline
from reranking.reranker import BaseReranker


class FakeExtractor:
    def embed_query(self, query):
        return [0.1, 0.2, 0.3], SparseVectorData(indices=[1, 2], values=[0.5, 0.4])


class RecordingManager:
    """Records which search primitive was used and returns fixed candidates."""

    def __init__(self, results):
        self.results = results
        self.calls = []

    def search_dense(self, **kwargs):
        self.calls.append(("dense", kwargs))
        return self.results

    def search_sparse(self, **kwargs):
        self.calls.append(("sparse", kwargs))
        return self.results

    def search_hybrid_rrf(self, **kwargs):
        self.calls.append(("hybrid", kwargs))
        return self.results


class RecordingReranker(BaseReranker):
    def __init__(self):
        self.calls = []

    def rerank(self, query, results, top_n=5):
        self.calls.append((query, [r.chunk_id for r in results], top_n))
        scores = [0.9, 0.1, 0.2, 0.0, 0.0][: len(results)]
        return self._rank(results, scores, top_n)


class FakeGenerator:
    """Never called: these tests stop at the context-selection step."""


def _candidates():
    return [
        HybridSearchResult(
            chunk_id=f"c{i}",
            text=f"text {i}",
            score=1.0 - i * 0.1,
            payload={"source_name": "s.md"},
        )
        for i in range(3)
    ]


def _pipeline(manager, *, reranker=None, top_n=2, **kwargs):
    return GroundedQAPipeline(
        db_manager=manager,
        extractor=FakeExtractor(),
        reranker=reranker,
        generator=FakeGenerator(),
        candidates=10,
        top_n=top_n,
        **kwargs,
    )


@pytest.mark.parametrize(
    "mode,expected",
    [("dense", "dense"), ("sparse", "sparse"), ("hybrid", "hybrid")],
)
def test_retrieval_mode_dispatches_to_the_matching_search(mode, expected):
    manager = RecordingManager(_candidates())
    pipeline = _pipeline(manager, reranker=RecordingReranker(), retrieval_mode=mode)

    pipeline.retrieve("query")

    assert [call[0] for call in manager.calls] == [expected]


def test_sparse_mode_passes_sparse_vector():
    manager = RecordingManager(_candidates())
    pipeline = _pipeline(manager, reranker=RecordingReranker(), retrieval_mode="sparse")

    pipeline.retrieve("query")

    _, kwargs = manager.calls[0]
    assert kwargs["sparse_indices"] == [1, 2]
    assert kwargs["sparse_values"] == [0.5, 0.4]


def test_unknown_retrieval_mode_is_rejected():
    with pytest.raises(ValueError, match="Unknown retrieval mode"):
        _pipeline(
            RecordingManager(_candidates()),
            reranker=RecordingReranker(),
            retrieval_mode="bm25",
        )


def test_rerank_false_skips_the_cross_encoder_and_the_model_load():
    pipeline = _pipeline(RecordingManager(_candidates()), reranker=None, rerank=False)

    assert pipeline.reranker is None
    context = pipeline.select_context("query", pipeline.retrieve("query"))

    assert [c.chunk_id for c in context] == ["c0", "c1"]
    assert [c.original_score for c in context] == [1.0, 0.9]


def test_rerank_true_uses_the_cross_encoder_ordering():
    reranker = RecordingReranker()
    pipeline = _pipeline(RecordingManager(_candidates()), reranker=reranker, top_n=2)

    context = pipeline.select_context("query", pipeline.retrieve("query"))

    assert reranker.calls == [("query", ["c0", "c1", "c2"], 2)]
    assert [c.chunk_id for c in context] == ["c0", "c2"]


def test_rerank_false_respects_top_n():
    pipeline = _pipeline(
        RecordingManager(_candidates()), reranker=None, rerank=False, top_n=1
    )

    context = pipeline.select_context("query", pipeline.retrieve("query"))

    assert [c.chunk_id for c in context] == ["c0"]
