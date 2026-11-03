"""FastAPI application exposing the Zenos grounded Q&A pipeline (Phase 4, point 3)."""

import json
import logging
import time
from typing import Iterator, List, Tuple

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from api.deps import get_pipeline
from api.schemas import (
    AnswerRequest,
    HealthResponse,
    InfoResponse,
    SearchHit,
    SearchRequest,
    SearchResponse,
)
from config import settings
from db.qdrant import HybridSearchResult, QdrantManager
from generation.pipeline import GroundedQAPipeline
from models import GroundedAnswer
from reranking.reranker import RerankResult

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zenos API",
    version="0.1.0",
    description="Hybrid RAG (dense+sparse RRF) + cross-encoder rerank + grounded cited answers.",
)


def _retrieve_and_rerank(
    pipeline: GroundedQAPipeline, query: str, top_k: int | None
) -> List[RerankResult]:
    candidates: List[HybridSearchResult] = pipeline.retrieve(query)
    return pipeline.reranker.rerank(query, candidates, top_n=top_k or pipeline.top_n)


@app.get("/")
def root() -> dict:
    return {"name": "Zenos API", "docs": "/docs", "health": "/health"}


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness/readiness probe — intentionally cheap (no model loading)."""
    try:
        points = QdrantManager().count_points(settings.qdrant_collection_name)
    except Exception as exc:  # noqa: BLE001 - surface a clear 503 for probes
        raise HTTPException(status_code=503, detail=f"Qdrant unavailable: {exc}") from exc
    return HealthResponse(status="ok", collection=settings.qdrant_collection_name, points=points)


@app.get("/info", response_model=InfoResponse)
def info(pipeline: GroundedQAPipeline = Depends(get_pipeline)) -> InfoResponse:
    return InfoResponse(
        provider=pipeline.generator.provider,
        model=pipeline.generator.model,
        reranker=type(pipeline.reranker).__name__,
        candidates=pipeline.candidates,
        top_n=pipeline.top_n,
        collection=settings.qdrant_collection_name,
    )


@app.post("/search", response_model=SearchResponse)
def search(
    request: SearchRequest, pipeline: GroundedQAPipeline = Depends(get_pipeline)
) -> SearchResponse:
    """Retrieval + rerank only (no LLM generation)."""
    reranked = _retrieve_and_rerank(pipeline, request.query, request.top_k)
    hits = [
        SearchHit(
            chunk_id=r.chunk_id,
            score=r.score,
            original_score=r.original_score,
            source_name=r.payload.get("source_name"),
            page_number=r.payload.get("page_number"),
            text=r.text,
        )
        for r in reranked
    ]
    return SearchResponse(query=request.query, results=hits)


@app.post("/answer", response_model=GroundedAnswer)
def answer(
    request: AnswerRequest, pipeline: GroundedQAPipeline = Depends(get_pipeline)
) -> GroundedAnswer:
    """Retrieve, rerank, and generate a grounded answer with validated citations."""
    reranked = _retrieve_and_rerank(pipeline, request.query, request.top_k)
    return pipeline.generator.generate(request.query, reranked)


@app.post("/answer/stream")
def answer_stream(
    request: AnswerRequest, pipeline: GroundedQAPipeline = Depends(get_pipeline)
) -> StreamingResponse:
    """Server-Sent Events: ``delta`` events with answer text, then a ``done`` event."""

    def event_stream() -> Iterator[str]:
        start = time.perf_counter()
        reranked = _retrieve_and_rerank(pipeline, request.query, request.top_k)

        first_token = None
        parts: List[str] = []
        for delta in pipeline.generator.stream(request.query, reranked):
            if first_token is None:
                first_token = time.perf_counter()
            parts.append(delta)
            yield f"data: {json.dumps({'type': 'delta', 'text': delta}, ensure_ascii=False)}\n\n"

        result = pipeline.generator.finalize(request.query, reranked, "".join(parts))
        ttft_ms = ((first_token or time.perf_counter()) - start) * 1000
        done = {
            "type": "done",
            "ttft_ms": round(ttft_ms, 1),
            "grounded": result.grounded,
            "refused": result.refused,
            "citations": [c.model_dump() for c in result.citations],
            "context_chunk_ids": result.context_chunk_ids,
        }
        yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
