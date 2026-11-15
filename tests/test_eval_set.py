"""Guards for the evaluation corpus and its ground truth.

These tests exist because the previous eval set hardcoded `doc_id` hashes: when a
corpus file changed, the ids silently stopped matching and recall collapsed to 0
with no error. Ground truth is now anchor-based, so drift fails loudly here.
"""

import re
from pathlib import Path

import pytest

from build_eval_set import QUESTIONS, build_sample_eval_set
from sample_corpus import load_corpus, resolve_anchors

EVAL_DIR = Path(__file__).parent.parent / "data" / "eval"
MIN_CORPUS_CHUNKS = 100


@pytest.fixture(scope="module")
def corpus():
    return load_corpus()


@pytest.fixture(scope="module")
def eval_set():
    return build_sample_eval_set()


def test_corpus_is_large_enough_to_measure_recall(corpus):
    """Recall@25 saturates on a tiny corpus — this guards the 6-chunk stub."""
    assert len(corpus) >= MIN_CORPUS_CHUNKS, f"corpus shrank to {len(corpus)} chunks"
    sources = {c.source_name for c in corpus}
    assert len(sources) >= 3, sources
    assert any(
        len({c.page_number for c in corpus if c.source_name == name}) > 1
        for name in sources
    ), "expected at least one multi-page document (page-level citations)"


def test_eval_set_is_eight_relevant_plus_one_negative(eval_set):
    assert len(eval_set) == len(QUESTIONS) == 9
    with_truth = [ev for ev in eval_set if ev["relevant"]]
    without_truth = [ev for ev in eval_set if not ev["relevant"]]
    assert len(with_truth) == 8
    assert len(without_truth) == 1


def test_every_ground_truth_id_exists_in_corpus(corpus, eval_set):
    known = {c.chunk_id for c in corpus}
    for entry in eval_set:
        for chunk_id in entry["relevant"]:
            assert chunk_id in known, f"{chunk_id} missing from corpus"


def test_each_relevant_question_resolves_to_a_few_chunks(eval_set):
    for entry in eval_set:
        if not entry["relevant"]:
            continue
        assert 1 <= len(entry["relevant"]) <= 3, entry["query"]


def test_negative_control_has_no_lexical_evidence(corpus, eval_set):
    negative = [ev for ev in eval_set if not ev["relevant"]]
    assert len(negative) == 1
    assert "process scheduling" not in " ".join(c.text.lower() for c in corpus)


def test_missing_anchor_raises_instead_of_scoring_zero(corpus):
    with pytest.raises(ValueError, match="not found in corpus"):
        resolve_anchors(corpus, ["this phrase is definitely absent"], question="drift")


def test_eval_set_module_has_no_hardcoded_doc_ids():
    """No literal 16-hex-char hash — that is how a stale ground truth sneaks back in."""
    text = (EVAL_DIR / "build_eval_set.py").read_text(encoding="utf-8")
    hashes = re.findall(r"\b[0-9a-f]{16}\b", text)
    assert not hashes, f"hardcoded doc_id hash(es) found: {hashes}"
