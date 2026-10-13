"""Prompt templates and context/citation helpers for grounded generation (Phase 3).

The prompt enforces the PRD's *"Strict Citation Generation"* requirement: the
model may only answer from the provided context, must attach a citation tag to
every declarative sentence, and must refuse when the context is insufficient.
"""

import re
from typing import Dict, List, Tuple

from models import Citation
from reranking.reranker import RerankResult

#: Exact sentence the model must return when the context does not answer the query.
REFUSAL_TEXT = "Saya tidak menemukan informasi ini di dalam dokumen yang tersedia."

SYSTEM_PROMPT = (
    "You are Zenos, a retrieval-grounded question answering assistant.\n\n"
    "STRICT RULES — follow every rule exactly:\n"
    "1. Answer ONLY using the information contained in the CONTEXT. Never use outside "
    "knowledge and never invent facts, sources, or page numbers.\n"
    "2. Answer in the SAME language as the user's question.\n"
    "3. Every declarative sentence MUST end with a citation tag in exactly this format: "
    "[Source: <source_name>, Pg <page_number>] — using the source_name and page_number "
    "given in the context blocks.\n"
    "4. If the CONTEXT does not contain enough information to answer the question, reply "
    f'with exactly this sentence and nothing else: "{REFUSAL_TEXT}"\n'
    "5. Be concise and factual. Do not add a citation when you refuse."
)

#: Matches citation tags like ``[Source: legal_uu_pdp_2022.md, Pg 1]``.
CITATION_PATTERN = re.compile(r"\[Source:\s*(.+?),\s*Pg\s*(\d+)\]", re.IGNORECASE)


def build_context(chunks: List[RerankResult]) -> str:
    """Render reranked chunks into numbered context blocks for the prompt."""
    if not chunks:
        return "(no context provided)"

    blocks: List[str] = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.payload.get("source_name", "unknown")
        page = chunk.payload.get("page_number", 1)
        blocks.append(
            f"[Chunk {i}]\n"
            f"source_name: {source}\n"
            f"page_number: {page}\n"
            f"chunk_id: {chunk.chunk_id}\n"
            f"text: {chunk.text}"
        )
    return "\n\n".join(blocks)


def build_user_message(query: str, context: str) -> str:
    """Compose the user turn: context followed by the question."""
    return f"CONTEXT:\n{context}\n\nQUESTION: {query}"


def _citation_index(chunks: List[RerankResult]) -> Dict[Tuple[str, int], str]:
    """Map ``(source_name_lower, page_number)`` -> chunk_id (first match wins)."""
    index: Dict[Tuple[str, int], str] = {}
    for chunk in chunks:
        source = str(chunk.payload.get("source_name", "")).strip().lower()
        try:
            page = int(chunk.payload.get("page_number", 1))
        except (TypeError, ValueError):
            page = 1
        index.setdefault((source, page), chunk.chunk_id)
    return index


def extract_citations(answer_text: str, chunks: List[RerankResult]) -> List[Citation]:
    """Extract citation tags from ``answer_text`` and keep only valid, deduped ones.

    A citation is valid when its ``(source_name, page_number)`` matches a chunk
    that was actually provided in the context; it is then resolved to that
    chunk's ``chunk_id``.
    """
    index = _citation_index(chunks)
    citations: List[Citation] = []
    seen: set = set()

    for match in CITATION_PATTERN.finditer(answer_text or ""):
        source = match.group(1).strip()
        page = int(match.group(2))
        chunk_id = index.get((source.lower(), page))
        if chunk_id is None or chunk_id in seen:
            continue
        seen.add(chunk_id)
        citations.append(
            Citation(source_name=source, page_number=page, chunk_id=chunk_id)
        )
    return citations


def is_refusal(answer_text: str) -> bool:
    """Return ``True`` when the answer is empty or the model refused to answer."""
    if not answer_text or not answer_text.strip():
        return True
    return REFUSAL_TEXT.lower() in answer_text.lower()
