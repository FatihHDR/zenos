"""Deterministic grounding metrics for PRD Section 6: groundedness and citation precision.

The PRD requires both metrics to be checkable **without** an LLM judge ("checked
deterministically via citation validation"). The proxies used here are:

* **Groundedness** — *"the ratio of claims that can be traced to the source text without
  external information"*. A claim is a sentence or list item in the answer; it counts as
  traced when it carries a citation tag that resolves to a chunk actually supplied as
  context.
* **Citation precision** — *"the proportion of generated citation tags that point to
  sources actually present in the provided context"*.

Why this needs its own implementation: ``extract_citations`` returns only the *valid*
citations and dedupes them per chunk, so it cannot tell you how many tags were emitted or
how many were wrong. These functions count the raw tags — including the ones the validator
throws away — which is exactly what a precision metric has to see.

Both metrics are only meaningful for answers that attempt an answer. Refusals contain no
claims to trace and are scored by refusal accuracy instead (see ``is_refusal``).
"""

import re
from dataclasses import dataclass
from typing import List, Sequence

from generation.prompts import CITATION_PATTERN, citation_index
from reranking.reranker import RerankResult

#: Claims end at sentence punctuation, or at a line break (bullet lists).
_CLAIM_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


@dataclass(frozen=True)
class GroundingMetrics:
    """Claim- and tag-level counts behind the two grounding ratios."""

    claims: int
    cited_claims: int
    tags: int
    valid_tags: int

    @property
    def groundedness(self) -> float:
        """Fraction of claims carrying a validated citation."""
        return self.cited_claims / self.claims if self.claims else 0.0

    @property
    def citation_precision(self) -> float:
        """Fraction of emitted citation tags that point at supplied context.

        An answer that emits no tags at all has no false tags, so this is ``1.0`` by
        convention — the missing citations are what groundedness measures.
        """
        return self.valid_tags / self.tags if self.tags else 1.0


def _raw_claims(answer_text: str) -> List[str]:
    """Claim segments with their citation tags still attached.

    The model reliably ends a claim with ``… diakhiri. [Source: x, Pg 1]`` — the sentence
    terminator lands *before* the tag. Splitting on punctuation alone would therefore
    strand every tag in a segment of its own and count every cited claim as uncited, so
    segments carrying nothing but tags are folded back into the preceding claim. Segments
    without a single alphanumeric character outside the tags (stray ``-`` bullets, quotes)
    are dropped so they cannot dilute the ratio.
    """
    claims: List[str] = []
    for segment in _CLAIM_SPLIT.split(answer_text or ""):
        normalized = " ".join(segment.split())
        text_only = CITATION_PATTERN.sub(" ", normalized).strip()
        if any(char.isalnum() for char in text_only):
            claims.append(normalized)
        elif claims and CITATION_PATTERN.search(normalized):
            claims[-1] = f"{claims[-1]} {normalized}"
        # A tag with no claim before it references nothing: ignore it.
    return claims


def split_claims(answer_text: str) -> List[str]:
    """Claim text with citation tags removed, e.g. ``"- Pelindungan"``."""
    return [
        CITATION_PATTERN.sub(" ", claim).strip() for claim in _raw_claims(answer_text)
    ]


def _has_valid_citation(claim: str, index) -> bool:
    """True when the claim carries at least one tag resolving to supplied context.

    A fabricated tag (wrong source or page) does **not** count as grounded — otherwise a
    hallucinated citation would inflate groundedness.
    """
    for match in CITATION_PATTERN.finditer(claim):
        source = match.group(1).strip().lower()
        page = int(match.group(2))
        if (source, page) in index:
            return True
    return False


def evaluate_grounding(
    answer_text: str, chunks: Sequence[RerankResult]
) -> GroundingMetrics:
    """Compute groundedness and citation precision for one answer."""
    index = citation_index(list(chunks))

    tags = 0
    valid_tags = 0
    for match in CITATION_PATTERN.finditer(answer_text or ""):
        tags += 1
        source = match.group(1).strip().lower()
        page = int(match.group(2))
        if (source, page) in index:
            valid_tags += 1

    claims = _raw_claims(answer_text)
    cited_claims = sum(1 for claim in claims if _has_valid_citation(claim, index))

    return GroundingMetrics(
        claims=len(claims),
        cited_claims=cited_claims,
        tags=tags,
        valid_tags=valid_tags,
    )
