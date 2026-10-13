"""Unit tests for the pure-Python Reciprocal Rank Fusion engine (Phase 2)."""

import pytest

from retrieval.rrf import (
    DEFAULT_RRF_K,
    reciprocal_rank_fusion,
    rrf_score,
)


def test_rrf_score_basic():
    # 1/(60+1) = 1/61
    assert rrf_score(1) == pytest.approx(1.0 / 61.0)
    # 1/(60+60) = 1/120
    assert rrf_score(60) == pytest.approx(1.0 / 120.0)
    assert rrf_score(1, k=5) == pytest.approx(1.0 / 6.0)


def test_rrf_score_invalid_rank_raises():
    with pytest.raises(ValueError):
        rrf_score(0)


def test_reciprocal_rank_fusion_simple():
    list_a = ["x", "y", "z"]
    list_b = ["y", "x", "w"]
    fused = reciprocal_rank_fusion([list_a, list_b])

    # x: 1/61 + 1/62 ; y: 1/62 + 1/61 -> equal scores, tie broken by best rank then insertion
    # x first seen in list a (rank 1), y first seen in list a (rank 2) -> x wins stable tie
    assert fused[0][0] == "x"
    assert fused[1][0] == "y"
    # z only in list a at rank 3 -> 1/63
    # w only in list b at rank 3 -> 1/63
    # both tie -> insertion order (z then w)

    scores = {item: score for item, score, _ in fused}
    assert scores["x"] == pytest.approx(1.0 / 61.0 + 1.0 / 62.0)
    assert scores["y"] == pytest.approx(1.0 / 62.0 + 1.0 / 61.0)
    assert scores["z"] == pytest.approx(1.0 / 63.0)
    assert scores["w"] == pytest.approx(1.0 / 63.0)


def test_reciprocal_rank_fusion_weights():
    list_a = ["a"]
    list_b = ["a"]
    # weight 2.0 on list a -> only a, score 2/61
    fused = reciprocal_rank_fusion([list_a, list_b], weights=[2.0, 1.0])
    assert fused[0][0] == "a"
    assert fused[0][1] == pytest.approx(2.0 / 61.0 + 1.0 / 61.0)


def test_reciprocal_rank_fusion_key():
    items_a = [{"id": "d1"}, {"id": "d2"}]
    items_b = [{"id": "d2"}]
    fused = reciprocal_rank_fusion([items_a, items_b], key=lambda d: d["id"])
    # d2 appears in both lists (rank 2 in a, rank 1 in b) so it beats d1
    # which appears only in list a at rank 1.
    assert [item["id"] for item, _, _ in fused] == ["d2", "d1"]
    scores = {item["id"]: score for item, score, _ in fused}
    assert scores["d1"] == pytest.approx(1.0 / 61.0)
    assert scores["d2"] == pytest.approx(1.0 / 62.0 + 1.0 / 61.0)


def test_reciprocal_rank_fusion_empty():
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []


def test_reciprocal_rank_fusion_duplicate_in_single_list():
    # duplicates within one list only count once (best rank)
    fused = reciprocal_rank_fusion([["x", "x"], ["x"]])
    assert fused[0][1] == pytest.approx(1.0 / 61.0 + 1.0 / 61.0)
    assert len(fused) == 1


def test_reciprocal_rank_fusion_weight_mismatch_raises():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([["a"], ["b"]], weights=[1.0])


def test_default_rrf_k_value():
    assert DEFAULT_RRF_K == 60