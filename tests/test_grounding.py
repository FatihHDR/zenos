"""Tests for the deterministic grounding metrics (groundedness, citation precision)."""

import pytest

from evaluation.grounding import evaluate_grounding, split_claims
from reranking.reranker import RerankResult


def _chunk(chunk_id: str, source: str, page: int, text: str = "isi chunk"):
    return RerankResult(
        chunk_id=chunk_id,
        text=text,
        score=1.0,
        payload={"source_name": source, "page_number": page},
    )


def test_split_claims_handles_sentences_and_bullet_lines():
    answer = (
        "Undang-Undang ini berasaskan delapan asas berikut:\n"
        "\n"
        "- Pelindungan [Source: uu.md, Pg 3]\n"
        "- Kepastian hukum [Source: uu.md, Pg 3]\n"
    )
    claims = split_claims(answer)

    assert len(claims) == 3
    assert claims[1] == "- Pelindungan"
    assert all("[Source" not in claim for claim in claims)


def test_split_claims_drops_empty_segments():
    assert split_claims("\n\n   \n") == []
    assert split_claims("") == []


def test_groundedness_counts_claims_with_valid_citations():
    chunks = [_chunk("c1", "uu.md", 3)]
    answer = (
        "Pasal 3 berasaskan delapan asas [Source: uu.md, Pg 3]. "
        "Asas pertama adalah pelindungan [Source: uu.md, Pg 3]. "
        "Kalimat ini tidak punya sitasi sama sekali."
    )
    metrics = evaluate_grounding(answer, chunks)

    assert metrics.claims == 3
    assert metrics.cited_claims == 2
    assert metrics.groundedness == pytest.approx(2 / 3)


def test_citation_precision_flags_tags_outside_the_context():
    chunks = [_chunk("c1", "uu.md", 3)]
    answer = (
        "Fakta benar [Source: uu.md, Pg 3]. "
        "Fakta lain [Source: uu.md, Pg 99]. "
        "Fakta ketiga [Source: bukan-konteks.md, Pg 1]."
    )
    metrics = evaluate_grounding(answer, chunks)

    assert metrics.tags == 3
    assert metrics.valid_tags == 1
    assert metrics.citation_precision == pytest.approx(1 / 3)


def test_citation_precision_is_one_when_no_tags_are_emitted():
    """No tags means no false tags; the missing citations are groundedness's job."""
    metrics = evaluate_grounding("Jawaban tanpa sitasi apa pun.", [_chunk("c1", "uu.md", 1)])

    assert metrics.tags == 0
    assert metrics.valid_tags == 0
    assert metrics.citation_precision == 1.0
    assert metrics.groundedness == 0.0


def test_bullet_list_answer_from_a_real_run():
    """Shape taken from an actual answer: one lead-in plus eight cited bullets."""
    chunks = [_chunk("c1", "legal_uu_pdp_2022.md", 3)]
    bullets = "\n".join(
        f"- {nama} [Source: legal_uu_pdp_2022.md, Pg 3]"
        for nama in (
            "Pelindungan",
            "Kepastian hukum",
            "Kepentingan umum",
            "Kemanfaatan",
            "Kehati-hatian",
            "Keseimbangan",
            "Pertanggungjawaban",
            "Kerahasiaan",
        )
    )
    answer = f"Undang-Undang ini berasaskan delapan asas berikut:\n\n{bullets}\n"
    metrics = evaluate_grounding(answer, chunks)

    assert metrics.claims == 9
    assert metrics.cited_claims == 8
    assert metrics.groundedness == pytest.approx(8 / 9)
    assert metrics.tags == 8
    assert metrics.citation_precision == 1.0


def test_tag_after_the_sentence_terminator_still_counts_as_cited():
    """Shape of real model output: the period lands *before* the tag."""
    chunks = [_chunk("c1", "uu.md", 24)]
    answer = (
        "Berdasarkan penjelasan Pasal 3, asas tersebut adalah:\n"
        "\n"
        "- **Asas pelindungan**: pemrosesan dilakukan dengan memberikan perlindungan. "
        "[Source: uu.md, Pg 24]\n"
        "- **Asas kepastian hukum**: pemrosesan dilakukan berdasarkan landasan hukum. "
        "[Source: uu.md, Pg 24]\n"
    )
    metrics = evaluate_grounding(answer, chunks)

    assert metrics.claims == 3
    assert metrics.cited_claims == 2
    assert metrics.groundedness == pytest.approx(2 / 3)


def test_tag_on_its_own_line_is_folded_into_the_claim():
    chunks = [_chunk("c1", "uu.md", 1)]
    metrics = evaluate_grounding("Fakta penting [Source: uu.md, Pg 1]\n[Source: uu.md, Pg 1]\n", chunks)

    assert metrics.claims == 1
    assert metrics.cited_claims == 1


def test_orphan_leading_tag_is_ignored():
    metrics = evaluate_grounding("[Source: uu.md, Pg 1]\n", [_chunk("c1", "uu.md", 1)])

    assert metrics.claims == 0
    assert metrics.groundedness == 0.0
    assert metrics.citation_precision == 1.0


def test_refusal_has_no_groundable_claims():
    """Refusals are scored by refusal accuracy, not by these ratios."""
    metrics = evaluate_grounding(
        "Saya tidak menemukan informasi ini di dalam dokumen yang tersedia.",
        [_chunk("c1", "uu.md", 1)],
    )

    assert metrics.cited_claims == 0
    assert metrics.groundedness == 0.0


def test_groundedness_is_zero_without_context():
    metrics = evaluate_grounding("Klaim [Source: uu.md, Pg 3].", [])

    assert metrics.cited_claims == 0
    assert metrics.groundedness == 0.0
    assert metrics.citation_precision == 0.0
