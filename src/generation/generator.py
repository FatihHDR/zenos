"""Grounded answer generation with strict citations (Phase 3).

Wraps the Anthropic Claude API and binds every answer to the retrieved context:
citations are validated against the chunks that were actually provided, and the
result is flagged as a refusal when no supporting context exists.
"""

import logging
from typing import Any, List, Optional

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


class GroundedGenerator:
    """Generates answers grounded in retrieved chunks using Anthropic Claude."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        client: Optional[Any] = None,
    ):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        self.temperature = settings.answer_temperature if temperature is None else temperature
        self.max_tokens = settings.answer_max_tokens if max_tokens is None else max_tokens

        if client is not None:
            self.client = client
        else:
            if not self.api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY is required for GroundedGenerator. "
                    "Set it in .env before generating answers."
                )
            import anthropic  # lazy: only when the real client is needed

            self.client = anthropic.Anthropic(api_key=self.api_key)

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
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(query, context)}],
        )

        text = self._extract_text(message)
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

    @staticmethod
    def _extract_text(message: Any) -> str:
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
