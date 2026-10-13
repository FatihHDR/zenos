"""Tests for the Phase 2 recall-evaluation harness (Recall@k metrics and eval set)."""

import pytest

from retrieval.metrics import (
    format_recall_report,
    mean_recall_at_k,
    precision_at_k,
    recall_at_k,
)


def test_recall_at_k_basic():
    retrieved = ["a", "b", "c", "d", "e"]
    relevant = ["b", "d"]
    assert recall_at_k(retrieved, relevant, k=2) == pytest.approx(0.5)
    assert recall_at_k(retrieved, relevant, k=5) == pytest.approx(1.0)
    assert recall_at_k(retrieved, relevant, k=1) == pytest.approx(0.0)


def test_recall_at_k_defaults_to_full():
    retrieved = ["a", "b", "c"]
    relevant = ["c"]
    assert recall_at_k(retrieved, relevant) == pytest.approx(1.0)


def test_recall_at_k_empty_relevant():
    assert recall_at_k(["a"], [], k=1) == 0.0


def test_recall_at_k_zero_k():
    assert recall_at_k(["a", "b"], ["a"], k=0) == 0.0


def test_precision_at_k():
    retrieved = ["a", "b", "c", "d"]
    relevant = ["a", "c", "x"]
    assert precision_at_k(retrieved, relevant, k=2) == pytest.approx(0.5)
    assert precision_at_k(retrieved, relevant, k=4) == pytest.approx(0.5)


def test_mean_recall_at_k():
    evals = [
        {"retrieved": ["a", "b"], "relevant": ["a"]},
        {"retrieved": ["x", "y"], "relevant": ["z"]},
    ]
    assert mean_recall_at_k(evals, k=1) == pytest.approx(0.5)
    assert mean_recall_at_k([], k=1) == 0.0


def test_format_recall_report_smoke():
    evals = [{"query": "test query", "retrieved": ["a"], "relevant": ["a"]}]
    report = format_recall_report(evals, k=25)
    assert "Query" in report
    assert "Recall@25" in report


def test_eval_set_well_formed():
    from build_eval_set import build_sample_eval_set

    eval_set = build_sample_eval_set()
    assert isinstance(eval_set, list)
    assert len(eval_set) > 0
    for ev in eval_set:
        assert "query" in ev
        assert "relevant" in ev
        assert isinstance(ev["query"], str)
        assert isinstance(ev["relevant"], list)