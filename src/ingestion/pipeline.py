"""End-to-end ingestion pipeline orchestrating parsing, chunking, dual embedding, and Qdrant storage."""

import logging
from pathlib import Path
from typing import List, Optional, Union
from rich.console import Console

from config import settings
from db.qdrant import QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor
from ingestion.chunker import TokenChunker
from ingestion.parser import DocumentParser
from models import DocumentChunk, IngestionResult

logger = logging.getLogger(__name__)
console = Console()


class IngestionPipeline:
    """Orchestrates parsing, token chunking, dual BGE-M3 embedding, and Qdrant injection."""

    def __init__(
        self,
        db_manager: Optional[QdrantManager] = None,
        embedding_extractor: Optional[BGEM3EmbeddingExtractor] = None,
        chunker: Optional[TokenChunker] = None,
        parser: Optional[DocumentParser] = None,
    ):
        self.db_manager = db_manager or QdrantManager()
        self.extractor = embedding_extractor or BGEM3EmbeddingExtractor()
        self.chunker = chunker or TokenChunker()
        self.parser = parser or DocumentParser()

    def prepare_db(self, recreate: bool = False) -> None:
        """Initialize collection in Qdrant."""
        self.db_manager.init_collection(recreate=recreate)

    def ingest_file(
        self,
        file_path: Union[str, Path],
        collection_name: Optional[str] = None,
    ) -> IngestionResult:
        """Ingest a single document file end-to-end."""
        path = Path(file_path)
        if not path.exists():
            return IngestionResult(
                doc_id="",
                source_name=path.name,
                num_chunks=0,
                success=False,
                error_message=f"File not found: {path}",
            )

        try:
            # 1. Parse document
            raw_doc = self.parser.parse_file(path)

            # 2. Chunk document (512 tokens with 100 token overlap)
            chunks = self.chunker.chunk_document(raw_doc)
            if not chunks:
                return IngestionResult(
                    doc_id=raw_doc.doc_id,
                    source_name=raw_doc.source_name,
                    num_chunks=0,
                    success=True,
                )

            # 3. Compute dual embeddings (Dense + Sparse BGE-M3)
            embedded_chunks = self.extractor.embed_chunks(chunks)

            # 4. Upsert into Qdrant
            self.db_manager.upsert_chunks(
                chunks=embedded_chunks,
                collection_name=collection_name,
            )

            return IngestionResult(
                doc_id=raw_doc.doc_id,
                source_name=raw_doc.source_name,
                num_chunks=len(embedded_chunks),
                success=True,
            )

        except Exception as e:
            logger.error(f"Error ingesting file {path}: {e}", exc_info=True)
            return IngestionResult(
                doc_id="",
                source_name=path.name,
                num_chunks=0,
                success=False,
                error_message=str(e),
            )

    def ingest_directory(
        self,
        directory_path: Union[str, Path],
        extensions: Optional[List[str]] = None,
        collection_name: Optional[str] = None,
    ) -> List[IngestionResult]:
        """Ingest all supported documents in a directory recursively."""
        dir_path = Path(directory_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")

        valid_exts = extensions or [".md", ".pdf", ".txt"]
        files: List[Path] = []
        for ext in valid_exts:
            files.extend(dir_path.rglob(f"*{ext}"))

        results: List[IngestionResult] = []
        for file in sorted(files):
            res = self.ingest_file(file, collection_name=collection_name)
            results.append(res)

        return results
