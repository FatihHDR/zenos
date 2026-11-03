"""Request/response schemas for the Zenos API (REST)."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, description="Query teks")
    top_k: Optional[int] = Field(default=None, ge=1, le=50, description="Jumlah hasil setelah rerank")


class SearchHit(BaseModel):
    chunk_id: str
    score: float
    original_score: Optional[float] = None
    source_name: Optional[str] = None
    page_number: Optional[int] = None
    text: str


class SearchResponse(BaseModel):
    query: str
    results: List[SearchHit]


class AnswerRequest(BaseModel):
    query: str = Field(min_length=1, description="Pertanyaan")
    top_k: Optional[int] = Field(default=None, ge=1, le=50, description="Jumlah chunk konteks setelah rerank")


class HealthResponse(BaseModel):
    status: str
    collection: str
    points: int


class InfoResponse(BaseModel):
    provider: str
    model: str
    reranker: str
    candidates: int
    top_n: int
    collection: str
