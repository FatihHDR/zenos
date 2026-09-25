"""Document parser for Markdown, Text, and PDF files."""

import hashlib
from pathlib import Path
from typing import List, Union
from models import DocumentPage, RawDocument


class DocumentParser:
    """Extracts raw text and per-page content from supported document formats."""

    @staticmethod
    def compute_doc_id(file_path: Union[str, Path], content_bytes: bytes) -> str:
        """Generate deterministic doc_id from file name and content hash."""
        path = Path(file_path)
        sha = hashlib.sha256(content_bytes).hexdigest()[:16]
        safe_name = path.stem.lower().replace(" ", "_")[:32]
        return f"{safe_name}_{sha}"

    def parse_markdown(self, file_path: Union[str, Path]) -> RawDocument:
        """Parse a markdown file into pages (by section or full document)."""
        path = Path(file_path)
        content_bytes = path.read_bytes()
        text = content_bytes.decode("utf-8", errors="replace")
        doc_id = self.compute_doc_id(path, content_bytes)

        # Markdown documents can be treated as a single page or split on major headers/page breaks
        pages: List[DocumentPage] = []
        if "---page---" in text:
            raw_pages = text.split("---page---")
            for idx, raw_page in enumerate(raw_pages, start=1):
                clean = raw_page.strip()
                if clean:
                    pages.append(DocumentPage(page_number=idx, text=clean))
        else:
            pages.append(DocumentPage(page_number=1, text=text.strip()))

        return RawDocument(
            doc_id=doc_id,
            source_name=path.name,
            file_type=path.suffix.lower(),
            pages=pages,
        )

    def parse_pdf(self, file_path: Union[str, Path]) -> RawDocument:
        """Parse a PDF document page by page."""
        path = Path(file_path)
        content_bytes = path.read_bytes()
        doc_id = self.compute_doc_id(path, content_bytes)
        pages: List[DocumentPage] = []

        # Try PyMuPDF first for high speed and accuracy
        try:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz

            doc = fitz.open(stream=content_bytes, filetype="pdf")
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_text = page.get_text().strip()
                if page_text:
                    pages.append(
                        DocumentPage(page_number=page_idx + 1, text=page_text)
                    )
            doc.close()
        except ImportError:
            # Fallback to pypdf
            import pypdf
            import io

            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            for page_idx, page in enumerate(reader.pages):
                page_text = (page.extract_text() or "").strip()
                if page_text:
                    pages.append(
                        DocumentPage(page_number=page_idx + 1, text=page_text)
                    )

        if not pages:
            # If no text could be extracted (e.g. empty or scanned)
            pages.append(DocumentPage(page_number=1, text=""))

        return RawDocument(
            doc_id=doc_id,
            source_name=path.name,
            file_type=".pdf",
            pages=pages,
        )

    def parse_text(self, file_path: Union[str, Path]) -> RawDocument:
        """Parse plain text file."""
        path = Path(file_path)
        content_bytes = path.read_bytes()
        text = content_bytes.decode("utf-8", errors="replace").strip()
        doc_id = self.compute_doc_id(path, content_bytes)

        return RawDocument(
            doc_id=doc_id,
            source_name=path.name,
            file_type=path.suffix.lower(),
            pages=[DocumentPage(page_number=1, text=text)],
        )

    def parse_file(self, file_path: Union[str, Path]) -> RawDocument:
        """Auto-detect format and parse file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()
        if suffix in [".md", ".markdown"]:
            return self.parse_markdown(path)
        elif suffix == ".pdf":
            return self.parse_pdf(path)
        elif suffix in [".txt", ".text"]:
            return self.parse_text(path)
        else:
            # Default to text reader
            return self.parse_text(path)
