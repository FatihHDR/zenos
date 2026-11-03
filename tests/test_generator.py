"""Tests for Phase 3 grounded generation (prompts + generator) using a fake Claude client."""

from unittest.mock import MagicMock

import pytest

from config import settings
from generation.generator import GroundedGenerator
from generation.prompts import (
    REFUSAL_TEXT,
    build_context,
    build_user_message,
    extract_citations,
    is_refusal,
)
from reranking.reranker import RerankResult


def _chunks():
    return [
        RerankResult(
            "legal_p1_c0",
            "Asas perlindungan data pribadi meliputi ...",
            0.9,
            original_score=0.5,
            payload={"source_name": "legal_uu_pdp_2022.md", "page_number": 1},
        ),
        RerankResult(
            "os_p1_c0",
            "Virtual memory allows ...",
            0.7,
            original_score=0.4,
            payload={"source_name": "os_virtual_memory.md", "page_number": 1},
        ),
    ]


def _fake_client(text):
    client = MagicMock()
    client.messages.create.return_value = MagicMock(content=[MagicMock(text=text)])
    return client


def test_build_context_includes_metadata():
    context = build_context(_chunks())
    assert "source_name: legal_uu_pdp_2022.md" in context
    assert "page_number: 1" in context
    assert "chunk_id: legal_p1_c0" in context
    assert "Asas perlindungan" in context


def test_build_context_empty():
    assert build_context([]) == "(no context provided)"


def test_build_user_message_contains_query():
    message = build_user_message("Apa itu?", "CONTEXT")
    assert "CONTEXT" in message
    assert "QUESTION: Apa itu?" in message


def test_extract_citations_valid_and_deduped():
    text = (
        "Asas ini wajib [Source: legal_uu_pdp_2022.md, Pg 1]. "
        "Diulang [Source: legal_uu_pdp_2022.md, Pg 1]."
    )
    citations = extract_citations(text, _chunks())
    assert len(citations) == 1
    assert citations[0].chunk_id == "legal_p1_c0"


def test_extract_citations_rejects_unknown_source():
    assert extract_citations("Ngarang [Source: ghost.md, Pg 9].", _chunks()) == []


def test_is_refusal():
    assert is_refusal(REFUSAL_TEXT) is True
    assert is_refusal("") is True
    assert is_refusal("Jawaban [Source: legal_uu_pdp_2022.md, Pg 1].") is False


def test_generate_grounded_answer():
    client = _fake_client("Data pribadi wajib dilindungi [Source: legal_uu_pdp_2022.md, Pg 1].")
    answer = GroundedGenerator(client=client, provider="anthropic").generate("Apa dasar?", _chunks())

    assert answer.grounded is True
    assert answer.refused is False
    assert [c.chunk_id for c in answer.citations] == ["legal_p1_c0"]
    assert answer.context_chunk_ids == ["legal_p1_c0", "os_p1_c0"]
    client.messages.create.assert_called_once()


def test_generate_refusal_skips_api_when_no_context():
    client = MagicMock()
    answer = GroundedGenerator(client=client, provider="anthropic").generate("Q", [])

    assert answer.refused is True
    assert answer.grounded is False
    assert answer.answer == REFUSAL_TEXT
    client.messages.create.assert_not_called()


def test_generate_refusal_from_model():
    answer = GroundedGenerator(client=_fake_client(REFUSAL_TEXT), provider="anthropic").generate("Q", _chunks())
    assert answer.refused is True
    assert answer.grounded is False
    assert answer.citations == []


def _fake_openai_client(text):
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=text))]
    )
    return client


def test_generate_openai_provider_grounded():
    client = _fake_openai_client("Data wajib dilindungi [Source: legal_uu_pdp_2022.md, Pg 1].")
    answer = GroundedGenerator(client=client, provider="openai").generate("Apa dasar?", _chunks())

    assert answer.grounded is True
    assert [c.chunk_id for c in answer.citations] == ["legal_p1_c0"]
    # OpenAI chat format: system + user messages
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_openai_provider_accepts_aliases():
    for alias in ("9router", "openai-compatible", "openrouter"):
        generator = GroundedGenerator(client=MagicMock(), provider=alias)
        assert generator.provider == alias


def test_openai_provider_default_model_is_auto(monkeypatch):
    monkeypatch.setattr(settings, "llm_model", None)
    generator = GroundedGenerator(client=MagicMock(), provider="openai")
    assert generator.model == "auto"


def test_unknown_provider_raises():
    with pytest.raises(ValueError):
        GroundedGenerator(client=MagicMock(), provider="bogus")
