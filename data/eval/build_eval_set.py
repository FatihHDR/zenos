"""Evaluation datasets for Phase 2: hybrid retrieval recall validation.

Each entry maps a natural-language query to the set of *document chunks* that
should be retrieved for it (the ground truth).  The relevant ids are the
deterministic ``chunk_id`` values produced by :class:`~ingestion.chunker.TokenChunker`
(``<doc_id>_p<page>_c<chunk>``), which are also stored in the Qdrant payload as
``chunk_id``, so relevance can be checked directly against retrieval output.

The doc ids are deterministic SHA-256 hashes computed by
``DocumentParser.compute_doc_id`` from the file name + content, so the ids below
stay valid as long as the bundled sample files are unchanged.  They can be
regenerated with::

    python data/eval/build_eval_set.py
"""

from typing import Dict, List

# Deterministic doc ids for the bundled sample documents (see module docstring).
LEGAL_DOC_ID = "legal_uu_pdp_2022_4cc242f7486b7104"
OS_VMEM_DOC_ID = "os_virtual_memory_4f264d95739fc9aa"
OS_PAGING_DOC_ID = "os_paging_overview_b9c77b1928a2de50"


def _chunk_id(doc_id: str, page: int, chunk: int) -> str:
    return f"{doc_id}_p{page}_c{chunk}"


def build_sample_eval_set() -> List[Dict[str, object]]:
    """Return the bundled recall-evaluation set for the sample documents.

    Chunk layout of the sample corpus (chunk_size=512, overlap=100):

    * ``legal_uu_pdp_2022`` — p1_c0: Pasal 3 (asas) + Pasal 4 (jenis data)
      + start of Pasal 20; p1_c1: remainder of Pasal 20 (dasar pemrosesan).
    * ``os_virtual_memory`` — p1_c0: sections 9.1–9.4 (benefits, paging HW,
      TLB, start of page-fault seq); p1_c1: remainder of section 9.4.
    * ``os_paging_overview`` (PDF) — p1_c0: section 1; p2_c1: section 2
      (chunk indices are global across pages, so page 2 starts at ``c1``).
    """
    return [
        # --- Legal / UU PDP ---
        {
            "query": "Apa saja asas Perlindungan Data Pribadi menurut UU PDP?",
            "relevant": [_chunk_id(LEGAL_DOC_ID, 1, 0)],
        },
        {
            "query": "Data pribadi yang bersifat spesifik itu apa saja?",
            "relevant": [_chunk_id(LEGAL_DOC_ID, 1, 0)],
        },
        {
            "query": "Apa dasar pemrosesan Data Pribadi oleh pengendali data?",
            "relevant": [
                _chunk_id(LEGAL_DOC_ID, 1, 0),
                _chunk_id(LEGAL_DOC_ID, 1, 1),
            ],
        },
        # --- OS: virtual memory ---
        {
            "query": "Keuntungan virtual memory seperti large address space dan demand paging",
            "relevant": [_chunk_id(OS_VMEM_DOC_ID, 1, 0)],
        },
        {
            "query": "Apa itu Translation Lookaside Buffer dan bedanya TLB hit dengan TLB miss?",
            "relevant": [_chunk_id(OS_VMEM_DOC_ID, 1, 0)],
        },
        {
            "query": "Bagaimana urutan penanganan page fault oleh kernel?",
            "relevant": [
                _chunk_id(OS_VMEM_DOC_ID, 1, 0),
                _chunk_id(OS_VMEM_DOC_ID, 1, 1),
            ],
        },
        # --- OS: paging (PDF, multi-page) ---
        {
            "query": "Bagaimana cara kerja paging dan address translation dengan MMU?",
            "relevant": [
                _chunk_id(OS_PAGING_DOC_ID, 1, 0),
                _chunk_id(OS_PAGING_DOC_ID, 2, 1),
            ],
        },
        {
            "query": "Apa perbedaan page dengan page frame?",
            "relevant": [_chunk_id(OS_PAGING_DOC_ID, 1, 0)],
        },
        # --- Negative control: no relevant chunk in the corpus ---
        {
            "query": "process scheduling mechanism in operating systems",
            "relevant": [],
        },
    ]


if __name__ == "__main__":  # pragma: no cover - convenience regenerator
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from ingestion.parser import DocumentParser
    from ingestion.chunker import TokenChunker

    parser = DocumentParser()
    chunker = TokenChunker()
    sample_dir = Path(__file__).parent.parent / "sample_docs"
    print("Deterministic sample-corpus ids:\n")
    for path in sorted(sample_dir.iterdir()):
        if path.is_file():
            doc = parser.parse_file(path)
            chunks = chunker.chunk_document(doc)
            print(f"{path.name}")
            print(f"  doc_id: {doc.doc_id}")
            for c in chunks:
                print(f"    {c.chunk_id}  ({c.metadata.token_count} tokens)")
