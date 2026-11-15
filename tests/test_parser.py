"""Tests for document parsing (Markdown, Text, PDF).

These use synthetic fixtures instead of the evaluation corpus. The corpus is
*derived* data (see ``scripts/fetch_corpus.py``) and is expected to change, so
asserting on its exact wording makes a parser unit test break for the wrong
reason — and silently stops testing the parser.
"""

from pathlib import Path

from ingestion.parser import DocumentParser


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_parse_markdown_splits_pages_on_separator(tmp_path):
    path = _write(
        tmp_path,
        "sample_doc.md",
        "# Bab I\n\nPasal 1.\n\n---page---\n\n# Bab II\n\nPasal 2.\n",
    )
    raw_doc = DocumentParser().parse_file(path)

    assert raw_doc.source_name == "sample_doc.md"
    assert raw_doc.file_type == ".md"
    assert [page.page_number for page in raw_doc.pages] == [1, 2]
    assert "Pasal 1." in raw_doc.pages[0].text
    assert "Pasal 2." in raw_doc.pages[1].text
    assert raw_doc.doc_id.startswith("sample_doc_")


def test_parse_markdown_without_separator_is_a_single_page(tmp_path):
    path = _write(tmp_path, "single.md", "# Judul\n\nIsi dokumen.\n")
    raw_doc = DocumentParser().parse_file(path)

    assert len(raw_doc.pages) == 1
    assert raw_doc.pages[0].page_number == 1


def test_parse_markdown_skips_empty_pages_but_keeps_numbering(tmp_path):
    path = _write(tmp_path, "sparse.md", "Halaman satu.\n\n---page---\n\n\n---page---\n\nHalaman tiga.\n")
    raw_doc = DocumentParser().parse_file(path)

    assert [page.page_number for page in raw_doc.pages] == [1, 3]


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
