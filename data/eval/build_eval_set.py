"""Evaluation dataset for the retrieval and generation experiments.

Ground truth is declared as **anchor phrases**, never as hardcoded chunk ids.
``doc_id`` is a SHA-256 hash of a corpus file's contents, so the previous
hardcoded ids went stale as soon as a corpus file was edited — and because a
stale id simply never matches, recall silently collapsed to 0 instead of
erroring. Anchors are resolved against the corpus at call time, so a stale
ground truth raises instead.

Anchor rules
------------
* Copy the phrase **verbatim from the chunk body** (whitespace is normalised, so
  PDF line wrapping is fine).
* Never anchor on an article *title*: the corpus header page lists every article
  title, so title anchors also match that header chunk.
* Keep anchors long enough to be distinctive; the resolution report printed by
  ``python data/eval/build_eval_set.py`` shows how many chunks each one matches.

Corpus: ``data/sample_docs/`` (UU PDP No. 27/2022 + English Wikipedia memory
articles + a small PDF). Rebuild it with ``python scripts/fetch_corpus.py``.
"""

from typing import Dict, List

from sample_corpus import load_corpus, resolve_anchors

# fmt: off
QUESTIONS: List[Dict[str, object]] = [
    # --- Indonesian statute: UU No. 27/2022 (UU PDP) ---
    {
        "query": "Apa saja asas Pelindungan Data Pribadi menurut UU PDP?",
        "anchors": ["Pasal 3 Undang-Undang ini berasaskan"],
        "evidence": "Pasal 3 — asas: pelindungan, kepastian hukum, kepentingan umum, dst.",
    },
    {
        "query": "Siapa yang dimaksud dengan Pengendali Data Pribadi?",
        "anchors": ["Pengendali Data Pribadi adalah"],
        "evidence": "Pasal 1 — definisi Pengendali Data Pribadi.",
    },
    {
        "query": "Sanksi administratif apa yang dikenakan kepada Pengendali Data Pribadi?",
        "anchors": ["Sanksi administratif sebagaimana dimaksud pada ayat (1) berupa"],
        "evidence": "Pasal 57 — peringatan tertulis, penghentian sementara, penghapusan data, denda.",
    },
    # --- English: virtual memory / paging ---
    {
        "query": "Apa manfaat utama virtual memory?",
        "anchors": ["idealized abstraction of the storage resources"],
        "evidence": "Wikipedia 'Virtual memory' — abstraksi sumber daya penyimpanan.",
    },
    {
        "query": "Apa itu Translation Lookaside Buffer dan bedanya TLB hit dengan TLB miss?",
        "anchors": ["Upon each virtual memory reference, the hardware checks the TLB"],
        "evidence": "Wikipedia 'Translation lookaside buffer' — jalur TLB hit vs TLB miss.",
    },
    {
        "query": "Bagaimana urutan penanganan page fault oleh sistem operasi?",
        "anchors": ["transparently retrying the instruction that caused the page fault"],
        "evidence": "Wikipedia 'Page fault' — muat halaman, perbarui page table, ulangi instruksi.",
    },
    {
        "query": "Bagaimana MMU menerjemahkan alamat virtual menjadi alamat fisik?",
        "anchors": ["computer hardware unit that examines all references to memory"],
        "evidence": "Wikipedia 'Memory management unit' — peran MMU dalam address translation.",
    },
    {
        "query": "Apa perbedaan page dengan page frame?",
        "anchors": ["Similarly, a page frame is the smallest fixed-length contiguous block of physical memory"],
        "evidence": "Wikipedia 'Page (computer memory)' — page = virtual, page frame = fisik.",
    },
    # --- Negative control: must be refused, not answered ---
    {
        "query": "process scheduling mechanism in operating systems",
        "anchors": [],
        "evidence": "Negative control: 'process scheduling' occurs in 0 corpus chunks.",
    },
]
# fmt: on


def build_sample_eval_set() -> List[Dict[str, object]]:
    """Resolve the anchors against the corpus and return the eval set.

    Raises ValueError if any anchor is missing, i.e. if the ground truth no longer
    matches the corpus.
    """
    chunks = load_corpus()
    eval_set: List[Dict[str, object]] = []
    for item in QUESTIONS:
        query = str(item["query"])
        anchors = list(item["anchors"])  # type: ignore[arg-type]
        eval_set.append(
            {
                "query": query,
                "relevant": resolve_anchors(chunks, anchors, question=query),
                "evidence": item["evidence"],
                "anchors": anchors,
            }
        )
    return eval_set


if __name__ == "__main__":  # pragma: no cover - human-readable report
    corpus = load_corpus()
    print(f"Corpus: {len(corpus)} chunks from data/sample_docs/\n")
    relevant_total = 0
    for entry in build_sample_eval_set():
        ids = entry["relevant"]
        relevant_total += len(ids)
        kind = "NEGATIVE CONTROL" if not ids else f"{len(ids)} relevant chunk(s)"
        print(f"* {entry['query']}")
        print(f"    {kind}  |  {entry['evidence']}")
        for chunk_id in ids:
            print(f"    - {chunk_id}")
    queries = len(QUESTIONS)
    print(
        f"\n{queries} questions ({queries - 1} relevant + 1 negative control), "
        f"{relevant_total} ground-truth chunk ids resolved."
    )
