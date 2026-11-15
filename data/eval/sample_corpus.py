"""Deterministic view over the sample corpus used by the evaluation set.

Ground truth is expressed as **anchor phrases**, never as hardcoded ids. The
``doc_id`` is a SHA-256 hash of the file contents, so editing any corpus file
silently invalidated the previously hardcoded ids — recall then collapsed to 0
without raising anything. Resolving anchors against the corpus fails loudly
instead: a missing anchor means the ground truth is stale, not that retrieval
performed badly.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from ingestion.chunker import TokenChunker  # noqa: E402
from ingestion.parser import DocumentParser  # noqa: E402

SAMPLE_DIR = ROOT / "data" / "sample_docs"


@dataclass(frozen=True)
class CorpusChunk:
    chunk_id: str
    source_name: str
    page_number: int
    chunk_index: int
    text: str


def _normalize(text: str) -> str:
    """Collapse whitespace and case so anchors survive PDF line-wrapping."""
    return " ".join(text.split()).casefold()


def load_corpus(sample_dir: Optional[Path] = None) -> List[CorpusChunk]:
    """Parse and chunk every file in ``data/sample_docs`` in deterministic order."""
    directory = Path(sample_dir) if sample_dir else SAMPLE_DIR
    parser, chunker = DocumentParser(), TokenChunker()

    chunks: List[CorpusChunk] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        document = parser.parse_file(path)
        for chunk in chunker.chunk_document(document):
            chunks.append(
                CorpusChunk(
                    chunk_id=chunk.chunk_id,
                    source_name=document.source_name,
                    page_number=chunk.metadata.page_number,
                    chunk_index=chunk.metadata.chunk_index,
                    text=chunk.text,
                )
            )
    return chunks


def resolve_anchors(
    chunks: Sequence[CorpusChunk],
    anchors: Iterable[str],
    *,
    question: str = "",
) -> List[str]:
    """Map anchor phrases to the chunk ids that contain them.

    Raises ValueError when an anchor matches nothing, so a stale ground truth
    fails fast instead of being scored as a retrieval miss.
    """
    resolved: List[str] = []
    missing: List[str] = []

    for anchor in anchors:
        needle = _normalize(anchor)
        hits = [c.chunk_id for c in chunks if needle in _normalize(c.text)]
        if not hits:
            missing.append(anchor)
        for chunk_id in hits:
            if chunk_id not in resolved:
                resolved.append(chunk_id)

    if missing:
        label = f" for question {question!r}" if question else ""
        raise ValueError(f"Anchor(s) not found in corpus{label}: {missing}")
    return resolved


def matched_chunks(
    chunks: Sequence[CorpusChunk], anchor: str
) -> List[CorpusChunk]:
    """Debug helper: the chunks containing ``anchor``."""
    needle = _normalize(anchor)
    return [c for c in chunks if needle in _normalize(c.text)]
