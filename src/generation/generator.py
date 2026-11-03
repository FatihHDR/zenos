"""Grounded answer generation with strict citations (Phase 3).

Two backends are supported, selected by ``LLM_PROVIDER``:

* ``anthropic`` (default) — Anthropic Claude via the ``anthropic`` SDK.
* ``openai`` — any **OpenAI-compatible** endpoint via the ``openai`` SDK, e.g.
  9router (``http://localhost:20128/v1``), OpenRouter, Groq, DeepSeek, or a
  local Ollama/LM Studio server. Set ``OPENAI_BASE_URL`` + ``OPENAI_API_KEY`` +
  ``LLM_MODEL``.

Both paths bind the answer to the retrieved context: citations are validated
against the chunks actually provided, and the result is flagged as a refusal
when no supporting context exists.
"""

import logging
from typing import Any, Iterator, List, Optional

from config import settings
from generation.prompts import (
    REFUSAL_TEXT,
    SYSTEM_PROMPT,
    build_context,
    build_user_message,
    extract_citations,
    is_refusal,
)
from models import GroundedAnswer
from reranking.reranker import RerankResult

logger = logging.getLogger(__name__)

_ANTHROPIC_PROVIDERS = {"anthropic", "claude"}
_OPENAI_PROVIDERS = {
    "openai",
    "openai-compatible",
    "openai_compatible",
    "9router",
    "openrouter",
    "groq",
    "deepseek",
    "ollama",
}


class GroundedGenerator:
    """Generates answers grounded in retrieved chunks, with validated citations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        client: Optional[Any] = None,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.provider = (provider or settings.llm_provider or "anthropic").strip().lower()
        if self.provider not in _ANTHROPIC_PROVIDERS and self.provider not in _OPENAI_PROVIDERS:
            raise ValueError(
                f"Unknown LLM provider {self.provider!r}. Expected one of "
                f"{sorted(_ANTHROPIC_PROVIDERS | _OPENAI_PROVIDERS)}."
            )
        self.temperature = settings.answer_temperature if temperature is None else temperature
        self.max_tokens = settings.answer_max_tokens if max_tokens is None else max_tokens
        self.model = model or self._default_model()

        if client is not None:
            self.client = client
        elif self.provider in _ANTHROPIC_PROVIDERS:
            key = api_key or settings.anthropic_api_key
            if not key:
                raise ValueError(
                    "ANTHROPIC_API_KEY is required for the Anthropic provider. "
                    "Set it in .env, or use LLM_PROVIDER=openai to route through an "
                    "OpenAI-compatible endpoint such as 9router."
                )
            import anthropic  # lazy: only when the Anthropic backend is used

            self.client = anthropic.Anthropic(api_key=key)
        else:  # OpenAI-compatible backend
            from openai import OpenAI  # lazy: only when the OpenAI backend is used

            # Local OpenAI-compatible routers (9router, Ollama) often run with auth
            # disabled; they still expect a non-empty key, so fall back to a dummy.
            key = api_key or settings.openai_api_key or "sk-9router"
            kwargs: dict = {"api_key": key}
            base = base_url or settings.openai_base_url
            if base:
                kwargs["base_url"] = base
            self.client = OpenAI(**kwargs)

    def _default_model(self) -> str:
        if self.provider in _ANTHROPIC_PROVIDERS:
            return settings.anthropic_model
        # 9router understands "auto" (picks a model by tier); override with LLM_MODEL.
        return settings.llm_model or "auto"

    def generate(self, query: str, chunks: List[RerankResult]) -> GroundedAnswer:
        """Answer ``query`` from ``chunks`` and return a validated ``GroundedAnswer``."""
        if not chunks:
            # Nothing retrieved -> refuse without spending an API call.
            return GroundedAnswer(
                query=query,
                answer=REFUSAL_TEXT,
                citations=[],
                context_chunk_ids=[],
                grounded=False,
                refused=True,
            )

        context = build_context(chunks)
        text = self._complete(SYSTEM_PROMPT, build_user_message(query, context))
        citations = extract_citations(text, chunks)
        refused = is_refusal(text)

        return GroundedAnswer(
            query=query,
            answer=text,
            citations=citations,
            context_chunk_ids=[c.chunk_id for c in chunks],
            grounded=bool(citations) and not refused,
            refused=refused,
        )

    def stream(self, query: str, chunks: List[RerankResult]) -> Iterator[str]:
        """Yield the answer token-by-token, grounded in ``chunks``.

        Mirrors :meth:`generate` but streams deltas, so callers can measure
        time-to-first-token and render progressively. Refuses (without an API
        call) when no context is available.
        """
        if not chunks:
            yield REFUSAL_TEXT
            return
        context = build_context(chunks)
        yield from self._stream_complete(
            SYSTEM_PROMPT, build_user_message(query, context)
        )

    def finalize(self, query: str, chunks: List[RerankResult], text: str) -> GroundedAnswer:
        """Build a validated ``GroundedAnswer`` from an already-generated ``text``."""
        citations = extract_citations(text, chunks)
        refused = is_refusal(text)
        return GroundedAnswer(
            query=query,
            answer=text,
            citations=citations,
            context_chunk_ids=[c.chunk_id for c in chunks],
            grounded=bool(citations) and not refused,
            refused=refused,
        )

    def _complete(self, system: str, user: str) -> str:
        """Send the prompt to the configured provider and return the answer text."""
        if self.provider in _ANTHROPIC_PROVIDERS:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return self._extract_anthropic_text(message)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return self._extract_openai_text(response)

    def _stream_complete(self, system: str, user: str) -> Iterator[str]:
        """Stream answer deltas from the configured provider."""
        if self.provider in _ANTHROPIC_PROVIDERS:
            stream = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
                stream=True,
            )
            for event in stream:
                text = self._extract_anthropic_delta(event)
                if text:
                    yield text
            return

        stream = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=True,
        )
        for chunk in stream:
            text = self._extract_openai_delta(chunk)
            if text:
                yield text

    @staticmethod
    def _extract_anthropic_delta(event: Any) -> str:
        """Read ``delta.text`` from an Anthropic streaming event (dict-friendly)."""
        delta = event.get("delta") if isinstance(event, dict) else getattr(event, "delta", None)
        if delta is None:
            return ""
        if isinstance(delta, dict):
            return delta.get("text") or ""
        return getattr(delta, "text", None) or ""

    @staticmethod
    def _extract_openai_delta(chunk: Any) -> str:
        """Read ``choices[0].delta.content`` from an OpenAI streaming chunk."""
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            return ""
        first = choices[0]
        delta = first.get("delta") if isinstance(first, dict) else getattr(first, "delta", None)
        if delta is None:
            return ""
        if isinstance(delta, dict):
            return delta.get("content") or ""
        return getattr(delta, "content", None) or ""

    @staticmethod
    def _extract_anthropic_text(message: Any) -> str:
        """Join the text blocks of an Anthropic message (supports dict-like fakes)."""
        parts: List[str] = []
        for block in getattr(message, "content", None) or []:
            if isinstance(block, dict):
                text = block.get("text")
            else:
                text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts).strip()

    @staticmethod
    def _extract_openai_text(response: Any) -> str:
        """Read ``choices[0].message.content`` from an OpenAI-style response."""
        choices = getattr(response, "choices", None) or []
        if not choices:
            return ""
        first = choices[0]
        message = first.get("message") if isinstance(first, dict) else getattr(first, "message", None)
        if message is None:
            return ""
        if isinstance(message, dict):
            return (message.get("content") or "").strip()
        return (getattr(message, "content", "") or "").strip()
