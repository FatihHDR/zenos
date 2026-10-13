"""Domain models and schemas for Zenos RAG."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata associated with a document chunk for strict citation and provenance."""

    doc_id: str = Field(description="Unique identifier for the document")
    source_name: str = Field(description="Original filename or title of the source document")
    page_number: int = Field(default=1, description="1-indexed page number where chunk originated")
    chunk_index: int = Field(default=0, description="Sequential 0-indexed position of chunk in document")
    total_chunks: int = Field(default=1, description="Total number of chunks created from document")
    token_count: int = Field(default=0, description="Number of tokens in the chunk text")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of chunk creation",
    )
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary additional metadata (e.g. section title, tags)",
    )


class DocumentChunk(BaseModel):
    """A granular chunk of text extracted from a document with dual embeddings."""

    chunk_id: str = Field(description="Unique deterministic identifier for the chunk")
    text: str = Field(description="Raw text content of the chunk")
    metadata: DocumentMetadata = Field(description="Metadata describing chunk provenance")
    dense_vector: Optional[List[float]] = Field(
        default=None, description="Dense vector embedding from BGE-M3 (1024-dim)"
    )
    sparse_indices: Optional[List[int]] = Field(
        default=None, description="Sparse vector token indices for BM25/BGE-M3 lexical weights"
    )
    sparse_values: Optional[List[float]] = Field(
        default=None, description="Sparse vector token weight values"
    )


class DocumentPage(BaseModel):
    """A single extracted page from a multi-page document."""

    page_number: int = Field(description="1-indexed page number")
    text: str = Field(description="Extracted text from this page")


class RawDocument(BaseModel):
    """An extracted document before chunking."""

    doc_id: str = Field(description="Unique document ID (hash or uuid)")
    source_name: str = Field(description="Source file path or name")
    file_type: str = Field(description="File extension or mime type (.pdf, .md, .txt)")
    pages: List[DocumentPage] = Field(default_factory=list, description="Extracted pages")


class IngestionResult(BaseModel):
    """Summary of document ingestion status."""

    doc_id: str
    source_name: str
    num_chunks: int = 0
    success: bool = True
    error_message: Optional[str] = None


class Citation(BaseModel):
    """A single source reference extracted from a grounded answer."""

    source_name: str = Field(description="Original filename or title of the cited source")
    page_number: int = Field(description="1-indexed page number cited")
    chunk_id: str = Field(description="Deterministic chunk id the citation resolves to")


class GroundedAnswer(BaseModel):
    """A generated answer bound to the retrieved context with verified citations."""

    query: str = Field(description="The user question that produced this answer")
    answer: str = Field(description="Generated answer text, with inline citations")
    citations: List[Citation] = Field(
        default_factory=list, description="Validated citations that map back to provided chunks"
    )
    context_chunk_ids: List[str] = Field(
        default_factory=list, description="Chunk ids supplied to the generator as context"
    )
    grounded: bool = Field(
        default=True, description="True when the answer carries at least one validated citation and is not a refusal"
    )
    refused: bool = Field(
        default=False, description="True when the generator refused to answer (no supporting context)"
    )
