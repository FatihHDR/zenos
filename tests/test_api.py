"""Tests for the Zenos FastAPI app (offline: fake pipeline + fake Qdrant manager)."""

import pytest
from fastapi.testclient import TestClient

import api.app as api_app
from api.app import app
from db.qdrant import HybridSearchResult
from models import Citation, GroundedAnswer
from reranking.reranker import RerankResult


class FakeReranker:
    def rerank(self, query, results, top_n=5):
        ranked = [
            RerankResult(r.chunk_id, r.text, score=r.score, original_score=r.score, payload=r.payload)
            for r in results
        ]
        return ranked[:top_n]


class FakeGenerator:
    provider = "openai"
    model = "test-model"

    @staticmethod
    def _citations(chunks):
        if not chunks:
            return []
        return [Citation(source_name="d.md", page_number=1, chunk_id=chunks[0].chunk_id)]

    def generate(self, query, chunks):
        return GroundedAnswer(
            query=query,
            answer="Jawaban [Source: d.md, Pg 1]",
            citations=self._citations(chunks),
            context_chunk_ids=[c.chunk_id for c in chunks],
            grounded=bool(chunks),
            refused=not chunks,
        )

    def stream(self, query, chunks):
        yield "Jawaban "
        yield "[Source: d.md, Pg 1]"

    def finalize(self, query, chunks, text):
        return GroundedAnswer(
            query=query,
            answer=text,
            citations=self._citations(chunks),
            context_chunk_ids=[c.chunk_id for c in chunks],
            grounded=bool(chunks),
            refused=False,
        )


class FakePipeline:
    def __init__(self):
        self.reranker = FakeReranker()
        self.generator = FakeGenerator()
        self.candidates = 25
        self.top_n = 5

    def retrieve(self, query):
        return [
            HybridSearchResult("c0", "text zero", 0.9, {"source_name": "d.md", "page_number": 1}),
            HybridSearchResult("c1", "text one", 0.5, {"source_name": "d.md", "page_number": 2}),
        ]


class FakeQdrantManager:
    def __init__(self, *args, **kwargs):
        pass

    def count_points(self, collection_name=None):
        return 3


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api_app, "QdrantManager", FakeQdrantManager)
    app.state.pipeline = FakePipeline()
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["points"] == 3


def test_info(client):
    body = client.get("/info").json()
    assert body["provider"] == "openai"
    assert body["model"] == "test-model"
    assert body["reranker"] == "FakeReranker"


def test_search(client):
    body = client.post("/search", json={"query": "apa itu"}).json()
    assert body["query"] == "apa itu"
    assert [h["chunk_id"] for h in body["results"]] == ["c0", "c1"]
    assert body["results"][0]["source_name"] == "d.md"


def test_answer(client):
    body = client.post("/answer", json={"query": "apa itu"}).json()
    assert body["grounded"] is True
    assert body["citations"][0]["chunk_id"] == "c0"


def test_answer_stream_sse(client):
    response = client.post("/answer/stream", json={"query": "apa itu"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    text = response.text
    assert '"type": "delta"' in text
    assert '"type": "done"' in text
    assert '"grounded": true' in text
