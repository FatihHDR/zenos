"""Token-aware document chunker preserving page metadata."""

import hashlib
from typing import List, Optional
import tiktoken

from config import settings
from models import DocumentChunk, DocumentMetadata, RawDocument


class TokenChunker:
    """Chunks documents with fixed token size and overlap, preserving page and source provenance."""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        tokenizer_name: Optional[str] = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

        self.tokenizer_name = tokenizer_name or settings.tokenizer_name
        try:
            self.tokenizer = tiktoken.get_encoding(self.tokenizer_name)
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a string."""
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def chunk_text(
        self,
        text: str,
        doc_id: str,
        source_name: str,
        page_number: int = 1,
        start_chunk_idx: int = 0,
    ) -> List[DocumentChunk]:
        """Split a single text/page into overlapping token chunks."""
        text = text.strip()
        if not text:
            return []

        tokens = self.tokenizer.encode(text)
        total_tokens = len(tokens)

        if total_tokens == 0:
            return []

        step = self.chunk_size - self.chunk_overlap
        token_slices: List[List[int]] = []

        if total_tokens <= self.chunk_size:
            token_slices.append(tokens)
        else:
            for start in range(0, total_tokens, step):
                end = min(start + self.chunk_size, total_tokens)
                token_slice = tokens[start:end]
                token_slices.append(token_slice)
                if end == total_tokens:
                    break

        chunks: List[DocumentChunk] = []
        for i, slice_tokens in enumerate(token_slices):
            chunk_text = self.tokenizer.decode(slice_tokens).strip()
            chunk_index = start_chunk_idx + i
            chunk_id = f"{doc_id}_p{page_number}_c{chunk_index}"

            metadata = DocumentMetadata(
                doc_id=doc_id,
                source_name=source_name,
                page_number=page_number,
                chunk_index=chunk_index,
                total_chunks=len(token_slices),
                token_count=len(slice_tokens),
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    metadata=metadata,
                )
            )

        return chunks

    def chunk_document(self, raw_doc: RawDocument) -> List[DocumentChunk]:
        """Chunk an entire RawDocument across all its pages."""
        all_chunks: List[DocumentChunk] = []
        current_chunk_idx = 0

        for page in raw_doc.pages:
            page_chunks = self.chunk_text(
                text=page.text,
                doc_id=raw_doc.doc_id,
                source_name=raw_doc.source_name,
                page_number=page.page_number,
                start_chunk_idx=current_chunk_idx,
            )
            all_chunks.extend(page_chunks)
            current_chunk_idx += len(page_chunks)

        # Update total_chunks count across all chunks in document
        total = len(all_chunks)
        for chunk in all_chunks:
            chunk.metadata.total_chunks = total

        return all_chunks
