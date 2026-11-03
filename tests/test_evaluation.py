"""Tests for Phase 4 evaluation helpers (offline; no Ragas calls or network)."""

import pytest

from evaluation.ragas_eval import (
    build_eval_records,
    compute_context_relevance,
    compute_recall_at_k,
)
from evaluation.ttft import measure_ttft, summarize
from models import Citation, GroundedAnswer
from reranking.reranker import RerankResult


def _answer(text, chunk_id="c0"):
    return GroundedAnswer(
        query="q",
        answer=text,
        citations=[Citation(source_name="doc.md", page_number=1, chunk_id=chunk_id)],
        context_chunk_ids=[chunk_id],
        grounded=True,
    )


class FakePipeline:
    def answer_with_context(self, query):
        return (
            [RerankResult("c1", "context text", 0.5, payload={})],
            _answer(f"ans for {query}", "c1"),
        )


class FakeGenerator:
    def finalize(self, query, chunks, text):
        return _answer(text, chunks[0].chunk_id if chunks else "c0")


class FakeStreamPipeline:
    def __init__(self):
        self.generator = FakeGenerator()

    def answer_streaming(self, query):
        return [RerankResult("c0", "ctx", 0.5, payload={})], iter(["Hel", "lo"])


def test_build_eval_records():
    eval_set = [
        {"query": "q1", "relevant": ["c1"]},
        {"query": "q2", "relevant": []},
    ]
    records = build_eval_records(FakePipeline(), eval_set)

    assert len(records) == 2
    assert records[0]["contexts"] == ["context text"]
    assert records[0]["chunk_ids"] == ["c1"]
    assert records[0]["ground_truth_ids"] == ["c1"]
    assert records[0]["grounded"] is True


def test_build_eval_records_limit():
    eval_set = [{"query": f"q{i}", "relevant": []} for i in range(5)]
    assert len(build_eval_records(FakePipeline(), eval_set, limit=2)) == 2


def test_compute_recall_at_k():
    records = [
        {"chunk_ids": ["a", "b", "c"], "ground_truth_ids": ["a"]},
        {"chunk_ids": ["x", "y"], "ground_truth_ids": ["z"]},
    ]
    assert compute_recall_at_k(records, k=2) == pytest.approx(0.5)


def test_compute_recall_at_k_skips_negative_controls():
    records = [
        {"chunk_ids": ["a"], "ground_truth_ids": ["a"]},
        {"chunk_ids": ["x"], "ground_truth_ids": []},
    ]
    assert compute_recall_at_k(records, k=5) == pytest.approx(1.0)


def test_compute_context_relevance():
    records = [{"chunk_ids": ["a", "b"], "ground_truth_ids": ["a"]}]
    assert compute_context_relevance(records, k=2) == pytest.approx(0.5)


def test_measure_ttft():
    row = measure_ttft(FakeStreamPipeline(), "q")

    assert row["answer"] == "Hello"
    assert row["ttft_ms"] >= 0
    assert row["total_ms"] >= row["ttft_ms"]
    assert row["grounded"] is True


def test_summarize_ttft():
    rows = [
        {"ttft_ms": 100.0, "retrieval_ms": 10.0},
        {"ttft_ms": 300.0, "retrieval_ms": 20.0},
        {"ttft_ms": 200.0, "retrieval_ms": 30.0},
    ]
    stats = summarize(rows)

    assert stats["count"] == 3
    assert stats["ttft_p50_ms"] == 200.0
    assert stats["ttft_max_ms"] == 300.0


def test_summarize_empty():
    assert summarize([])["count"] == 0
