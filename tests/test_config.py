"""Tests for configuration settings."""

import pytest

from config import Settings


@pytest.fixture
def isolated_cwd(tmp_path, monkeypatch):
    """Move away from the project .env file so we assert the code-level defaults.

    ``Settings`` reads ``.env`` relative to the current directory, and the
    project's .env intentionally overrides host/port — so a defaults test must
    run somewhere else (and without those env vars set).
    """
    monkeypatch.chdir(tmp_path)
    for key in ("QDRANT_HOST", "QDRANT_PORT", "QDRANT_GRPC_PORT"):
        monkeypatch.delenv(key, raising=False)
    return tmp_path


def test_default_settings(isolated_cwd):
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
