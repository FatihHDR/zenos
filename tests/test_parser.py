"""Tests for document parsing (Markdown, Text, PDF)."""

from pathlib import Path
from ingestion.parser import DocumentParser


def test_parse_markdown():
    parser = DocumentParser()
    md_file = Path("data/sample_docs/legal_uu_pdp_2022.md")
    assert md_file.exists()

    raw_doc = parser.parse_file(md_file)
    assert raw_doc.source_name == "legal_uu_pdp_2022.md"
    assert raw_doc.file_type == ".md"
    assert len(raw_doc.pages) >= 1
    assert "Perlindungan Data Pribadi" in raw_doc.pages[0].text
    assert raw_doc.doc_id.startswith("legal_uu_pdp_2022_")


def test_parse_pdf():
    parser = DocumentParser()
    pdf_file = Path("data/sample_docs/os_paging_overview.pdf")
    assert pdf_file.exists()

    raw_doc = parser.parse_file(pdf_file)
    assert raw_doc.source_name == "os_paging_overview.pdf"
    assert raw_doc.file_type == ".pdf"
    assert len(raw_doc.pages) == 2
    assert "Operating Systems Principles" in raw_doc.pages[0].text
    assert "Page Replacement Algorithms" in raw_doc.pages[1].text
