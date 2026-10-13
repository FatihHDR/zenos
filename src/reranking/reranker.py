"""Cross-encoder reranking for Phase 3.

Phase 3 of the PRD asks to *"filter the 25 RRF result documents into the 5 chunks
with the highest relevance"* using a cross-encoder reranker.  Two backends are
provided:

* :class:`CohereReranker` — Cohere Rerank 3 API (``rerank-multilingual-v3.0`` by
  default), used when ``COHERE_API_KEY`` is configured.
* :class:`LocalCrossEncoderReranker` — local ``BAAI/bge-reranker-v2-m3`` via
  FlagEmbedding, used as the offline fallback so the pipeline runs without any
  API key.

:func:`get_reranker` picks the backend from ``RERANK_PROVIDER`` (``auto`` by
default: Cohere when a key is present, otherwise local).
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from config import settings
from db.qdrant import HybridSearchResult

logger = logging.getLogger(__name__)


class RerankResult:
    """A single reranked candidate produced by a cross-encoder."""

    __slots__ = ("chunk_id", "text", "score", "original_score", "payload")

    def __init__(
        self,
        chunk_id: str,
        text: str,
        score: float,
        original_score: Optional[float] = None,
        payload: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.score = score
        self.original_score = original_score
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "score": self.score,
            "original_score": self.original_score,
            "metadata": self.payload,
        }

    def __repr__(self) -> str:
        return f"RerankResult(chunk_id={self.chunk_id!r}, score={self.score:.4f})"


class BaseReranker(ABC):
    """Interface shared by every reranker backend."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: List[HybridSearchResult],
        top_n: int = 5,
    ) -> List[RerankResult]:
        """Re-score ``results`` for ``query`` and return the best ``top_n``."""

    @staticmethod
    def _rank(
        results: List[HybridSearchResult],
        scores: List[float],
        top_n: int,
    ) -> List[RerankResult]:
        """Order candidates by reranker score (descending) and keep the top ``top_n``.

        Pure and dependency-free so the ranking logic can be unit-tested without
        loading a model or calling an API.  Ties keep the original retrieval order
        (stable sort).
        """
        if not results:
            return []
        top_n = max(0, min(top_n, len(results)))
        if top_n == 0:
            return []

        order = sorted(range(len(results)), key=lambda i: scores[i], reverse=True)
        ranked: List[RerankResult] = []
        for i in order[:top_n]:
            source = results[i]
            ranked.append(
                RerankResult(
                    chunk_id=source.chunk_id,
                    text=source.text,
                    score=float(scores[i]),
                    original_score=float(source.score),
                    payload=source.payload,
                )
            )
        return ranked


class CohereReranker(BaseReranker):
    """Reranker backed by the Cohere Rerank 3 API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        client: Optional[Any] = None,
    ):
        self.api_key = api_key or settings.cohere_api_key
        self.model = model or settings.cohere_rerank_model
        if client is not None:
            self.client = client
        else:
            if not self.api_key:
                raise ValueError(
                    "COHERE_API_KEY is required for CohereReranker. "
                    "Set it in .env or use RERANK_PROVIDER=local."
                )
            import cohere  # lazy: only when the Cohere backend is actually used

            self.client = cohere.Client(api_key=self.api_key)

    def rerank(
        self,
        query: str,
        results: List[HybridSearchResult],
        top_n: int = 5,
    ) -> List[RerankResult]:
        if not results:
            return []
        top_n = max(0, min(top_n, len(results)))
        if top_n == 0:
            return []

        documents = [r.text for r in results]
        response = self.client.rerank(
            model=self.model,
            query=query,
            documents=documents,
            top_n=top_n,
        )

        scores = [0.0] * len(results)
        for item in response.results:
            scores[item.index] = float(item.relevance_score)
        return self._rank(results, scores, top_n)


class LocalCrossEncoderReranker(BaseReranker):
    """Reranker backed by a local cross-encoder (``BAAI/bge-reranker-v2-m3``)."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        use_fp16: bool = False,
        device: Optional[str] = None,
        model: Optional[Any] = None,
    ):
        self.model_name = model_name or settings.rerank_local_model
        self.use_fp16 = use_fp16
        self.device = device
        if model is not None:
            self.model = model
        else:
            from FlagEmbedding import FlagReranker  # lazy: heavy import

            logger.info(f"Loading local cross-encoder reranker ({self.model_name})...")
            self.model = FlagReranker(
                self.model_name,
                use_fp16=self.use_fp16,
                device=self.device,
            )

    def rerank(
        self,
        query: str,
        results: List[HybridSearchResult],
        top_n: int = 5,
    ) -> List[RerankResult]:
        if not results:
            return []
        top_n = max(0, min(top_n, len(results)))
        if top_n == 0:
            return []

        pairs = [[query, r.text] for r in results]
        scores = self.model.compute_score(pairs, normalize=True)
        if isinstance(scores, (int, float)):
            scores = [scores]
        return self._rank(results, [float(s) for s in scores], top_n)


def get_reranker(provider: Optional[str] = None, **kwargs: Any) -> BaseReranker:
    """Build a reranker from ``RERANK_PROVIDER`` (``auto`` picks based on the key)."""
    selected = (provider or settings.rerank_provider or "auto").lower()

    if selected == "cohere":
        return CohereReranker(**kwargs)
    if selected == "local":
        return LocalCrossEncoderReranker(**kwargs)
    if selected == "auto":
        if settings.cohere_api_key:
            return CohereReranker(**kwargs)
        return LocalCrossEncoderReranker(**kwargs)

    raise ValueError(
        f"Unknown rerank provider {selected!r}. Expected 'auto', 'cohere' or 'local'."
    )
