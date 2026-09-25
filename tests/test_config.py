"""Tests for configuration settings."""

from config import Settings


def test_default_settings():
    settings = Settings()
    assert settings.qdrant_host == "localhost"
    assert settings.qdrant_port == 6333
    assert settings.dense_model_name == "BAAI/bge-m3"
    assert settings.sparse_model_name == "BAAI/bge-m3"
    assert settings.dense_vector_name == "dense"
    assert settings.sparse_vector_name == "sparse"
    assert settings.embedding_dimension == 1024
    assert settings.chunk_size == 512
    assert settings.chunk_overlap == 100
