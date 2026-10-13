"""Tests for the Phase 3 cross-encoder reranking backends."""

from unittest.mock import MagicMock

import pytest

import reranking.reranker as reranker_module
from config import settings
from db.qdrant import HybridSearchResult
from reranking.reranker import (
    BaseReranker,
    CohereReranker,
    LocalCrossEncoderReranker,
    RerankResult,
    get_reranker,
)


def _results():
    return [
        HybridSearchResult("c0", "alpha", 0.5, {"source_name": "a.md", "page_number": 1}),
        HybridSearchResult("c1", "beta", 0.4, {"source_name": "b.md", "page_number": 2}),
        HybridSearchResult("c2", "gamma", 0.3, {"source_name": "c.md", "page_number": 3}),
    ]


def test_rank_orders_by_score_desc_and_clamps():
    ranked = BaseReranker._rank(_results(), [0.1, 0.9, 0.5], top_n=2)
    assert [r.chunk_id for r in ranked] == ["c1", "c2"]
    assert ranked[0].score == pytest.approx(0.9)
    assert ranked[0].original_score == pytest.approx(0.4)
    assert ranked[0].payload["source_name"] == "b.md"


def test_rank_empty_and_zero_top_n():
    assert BaseReranker._rank([], [], top_n=5) == []
    assert BaseReranker._rank(_results(), [1.0, 2.0, 3.0], top_n=0) == []


def test_rerank_result_to_dict():
    result = RerankResult("c0", "text", 1.0, original_score=0.2, payload={"k": "v"})
    data = result.to_dict()
    assert data["chunk_id"] == "c0"
    assert data["score"] == 1.0
    assert data["original_score"] == 0.2
    assert data["metadata"] == {"k": "v"}


def test_cohere_reranker_with_injected_client():
    client = MagicMock()
    top = MagicMock(index=2, relevance_score=0.99)
    second = MagicMock(index=0, relevance_score=0.10)
    client.rerank.return_value = MagicMock(results=[top, second])

    ranked = CohereReranker(api_key="x", client=client).rerank("query", _results(), top_n=2)

    assert [r.chunk_id for r in ranked] == ["c2", "c0"]
    kwargs = client.rerank.call_args.kwargs
    assert kwargs["query"] == "query"
    assert kwargs["documents"] == ["alpha", "beta", "gamma"]
    assert kwargs["top_n"] == 2


def test_cohere_reranker_requires_key():
    with pytest.raises(ValueError):
        CohereReranker(api_key=None, client=None)


def test_local_reranker_with_injected_model():
    model = MagicMock()
    model.compute_score.return_value = [0.2, 0.8, 0.5]
    ranked = LocalCrossEncoderReranker(model=model).rerank("query", _results(), top_n=2)
    assert [r.chunk_id for r in ranked] == ["c1", "c2"]


def test_get_reranker_auto_prefers_cohere_with_key(monkeypatch):
    monkeypatch.setattr(settings, "rerank_provider", "auto")
    monkeypatch.setattr(settings, "cohere_api_key", "key")
    monkeypatch.setattr(reranker_module, "CohereReranker", lambda **kw: ("cohere", kw))
    monkeypatch.setattr(reranker_module, "LocalCrossEncoderReranker", lambda **kw: ("local", kw))
    assert get_reranker() == ("cohere", {})


def test_get_reranker_auto_falls_back_to_local(monkeypatch):
    monkeypatch.setattr(settings, "rerank_provider", "auto")
    monkeypatch.setattr(settings, "cohere_api_key", None)
    monkeypatch.setattr(reranker_module, "CohereReranker", lambda **kw: ("cohere", kw))
    monkeypatch.setattr(reranker_module, "LocalCrossEncoderReranker", lambda **kw: ("local", kw))
    assert get_reranker() == ("local", {})


def test_get_reranker_explicit_provider(monkeypatch):
    monkeypatch.setattr(reranker_module, "CohereReranker", lambda **kw: ("cohere", kw))
    monkeypatch.setattr(reranker_module, "LocalCrossEncoderReranker", lambda **kw: ("local", kw))
    assert get_reranker("cohere") == ("cohere", {})
    assert get_reranker("local") == ("local", {})


def test_get_reranker_unknown_raises():
    with pytest.raises(ValueError):
        get_reranker("bogus")
