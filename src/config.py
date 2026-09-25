"""Configuration settings for Zenos."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Qdrant Database Configuration
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_grpc_port: int = Field(default=6334, alias="QDRANT_GRPC_PORT")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(default="zenos_docs", alias="QDRANT_COLLECTION_NAME")
    qdrant_use_local_memory: bool = Field(default=False, alias="QDRANT_USE_LOCAL_MEMORY")
    qdrant_local_path: Optional[str] = Field(default=None, alias="QDRANT_LOCAL_PATH")

    # Embedding Model Configuration
    dense_model_name: str = Field(default="BAAI/bge-m3", alias="DENSE_MODEL_NAME")
    sparse_model_name: str = Field(default="BAAI/bge-m3", alias="SPARSE_MODEL_NAME")
    dense_vector_name: str = Field(default="dense", alias="DENSE_VECTOR_NAME")
    sparse_vector_name: str = Field(default="sparse", alias="SPARSE_VECTOR_NAME")
    embedding_dimension: int = Field(default=1024, alias="EMBEDDING_DIMENSION")

    # Chunking Configuration (PRD: 512 tokens with 100 token overlap)
    chunk_size: int = Field(default=512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    tokenizer_name: str = Field(default="cl100k_base", alias="TOKENIZER_NAME")

    # Storage Paths
    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")
    cache_dir: Optional[Path] = Field(default=None, alias="CACHE_DIR")


# Global singleton settings instance
settings = Settings()
