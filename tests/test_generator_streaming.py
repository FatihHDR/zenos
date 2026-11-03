"""Tests for Phase 4 streaming generation (both providers, offline)."""

from unittest.mock import MagicMock

from generation.generator import GroundedGenerator
from generation.prompts import REFUSAL_TEXT
from reranking.reranker import RerankResult


def _chunks():
    return [
        RerankResult(
            "legal_p1_c0",
            "Asas perlindungan data pribadi.",
            0.9,
            payload={"source_name": "legal_uu_pdp_2022.md", "page_number": 1},
        )
    ]


def test_stream_anthropic_provider():
    client = MagicMock()
    client.messages.create.return_value = iter(
        [
            {"type": "content_block_delta", "delta": {"text": "Asas "}},
            {"type": "content_block_delta", "delta": {"text": "[Source: legal_uu_pdp_2022.md, Pg 1]."}},
        ]
    )
    generator = GroundedGenerator(client=client, provider="anthropic")

    text = "".join(generator.stream("q", _chunks()))

    assert text == "Asas [Source: legal_uu_pdp_2022.md, Pg 1]."
    assert client.messages.create.call_args.kwargs["stream"] is True


def test_stream_openai_provider():
    client = MagicMock()
    client.chat.completions.create.return_value = iter(
        [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Data "))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content="wajib."))]),
        ]
    )
    generator = GroundedGenerator(client=client, provider="openai")

    text = "".join(generator.stream("q", _chunks()))

    assert text == "Data wajib."
    assert client.chat.completions.create.call_args.kwargs["stream"] is True


def test_stream_empty_context_refuses_without_call():
    client = MagicMock()
    generator = GroundedGenerator(client=client, provider="anthropic")

    text = "".join(generator.stream("q", []))

    assert text == REFUSAL_TEXT
    client.messages.create.assert_not_called()


def test_finalize_builds_grounded_answer():
    generator = GroundedGenerator(client=MagicMock(), provider="anthropic")
    answer = generator.finalize(
        "q", _chunks(), "Asas perlindungan data [Source: legal_uu_pdp_2022.md, Pg 1]."
    )

    assert answer.grounded is True
    assert answer.refused is False
    assert [c.chunk_id for c in answer.citations] == ["legal_p1_c0"]


def test_finalize_refusal():
    generator = GroundedGenerator(client=MagicMock(), provider="anthropic")
    answer = generator.finalize("q", _chunks(), REFUSAL_TEXT)

    assert answer.refused is True
    assert answer.grounded is False
