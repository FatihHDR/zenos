"""Build the sample corpus in ``data/sample_docs/`` from public sources.

Why a script: the corpus is *derived* data, so its provenance must be reproducible.
It also replaces the earlier hand-written stubs (a few KB) with real documents so
that retrieval metrics are meaningful (Recall@25 saturates on a 6-chunk corpus).

Sources
-------
* ``legal_uu_pdp_2022.md`` — UU No. 27/2022 (Pelindungan Data Pribadi), downloaded as
  PDF and converted page-by-page to Markdown with ``---page---`` separators so page
  numbers survive for citations. Indonesian statutes carry no copyright
  (UU No. 28/2014, Pasal 42).
* ``os_virtual_memory.md`` — English Wikipedia articles (CC BY-SA 4.0), one article per
  page, attribution in the file header.

Run: ``python scripts/fetch_corpus.py``
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SAMPLE_DIR = ROOT / "data" / "sample_docs"

LAW_URL = (
    "https://learning.hukumonline.com/wp-content/uploads/2023/07/"
    "Undang-Undang-No.27-Tahun-2022-Hukumonline.pdf"
)
LAW_PDF = RAW_DIR / "uu_pdp_2022.pdf"
LAW_OUT = SAMPLE_DIR / "legal_uu_pdp_2022.md"

WIKI_TITLES = [
    "Virtual memory",
    "Memory paging",
    "Page fault",
    "Translation lookaside buffer",
    "Memory management unit",
    "Page replacement algorithm",
    "Demand paging",
    "Memory protection",
    "Thrashing (computer science)",
    "Swap (computer science)",
    "Memory address",
    "Memory segmentation",
    "Page (computer memory)",
    "Working set",
    "Fragmentation (computing)",
    "CPU cache",
    "Virtual address space",
    "X86 memory segmentation",
]
WIKI_OUT = SAMPLE_DIR / "os_virtual_memory.md"

PAGE_SEPARATOR = "\n\n---page---\n\n"
USER_AGENT = "zenos-course-corpus/1.0 (educational use)"


def download(url: str, dest: Path, *, force: bool = False) -> Path:
    if dest.exists() and not force:
        print(f"  cached: {dest.relative_to(ROOT)}")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as fh:
        fh.write(resp.read())
    print(f"  downloaded: {dest.relative_to(ROOT)} ({dest.stat().st_size // 1024} KB)")
    return dest


def build_law() -> Path:
    """Convert the statute PDF into Markdown, one page per `---page---` block."""
    import pymupdf

    print("legal_uu_pdp_2022.md")
    download(LAW_URL, LAW_PDF)

    doc = pymupdf.open(LAW_PDF)
    pages = [page.get_text().strip() for page in doc]
    header = (
        "# UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi\n\n"
        "Sumber: peraturan perundang-undangan Republik Indonesia "
        "(diunduh dari hukumonline.com). Peraturan perundang-undangan tidak "
        "dilindungi hak cipta (UU No. 28/2014 Pasal 42).\n"
    )
    pages[0] = f"{header}\n{pages[0]}"

    LAW_OUT.write_text(PAGE_SEPARATOR.join(p for p in pages if p), encoding="utf-8")
    print(f"  pages: {len(pages)}  chars: {sum(len(p) for p in pages):,}")
    return LAW_OUT


def _wiki_extract(title: str, *, attempts: int = 5) -> tuple[str, str] | None:
    """Return (canonical_title, plain_text) or None."""
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "exlimit": "max",
            "redirects": 1,
            "format": "json",
            "titles": title,
        }
    )
    url = f"https://en.wikipedia.org/w/api.php?{params}"
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.load(resp)
            for page in data.get("query", {}).get("pages", {}).values():
                text = (page.get("extract") or "").strip()
                if len(text) > 2000:
                    return page.get("title", title), text
            return None
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503) and attempt < attempts - 1:
                wait = 2 ** (attempt + 1)
                print(f"  {exc.code} on '{title}', retry in {wait}s")
                time.sleep(wait)
                continue
            raise
    return None


def build_os() -> Path:
    """Fetch the Wikipedia articles, one per page, with attribution."""
    print("os_virtual_memory.md")
    articles: list[tuple[str, str]] = []
    seen: set[str] = set()

    for title in WIKI_TITLES:
        try:
            result = _wiki_extract(title)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"  FAILED {title}: {exc}")
            continue
        if not result:
            print(f"  skipped {title} (no extract)")
            continue
        canonical, text = result
        if canonical in seen:
            print(f"  duplicate {title} -> {canonical}")
            continue
        seen.add(canonical)
        articles.append((canonical, text))
        print(f"  ok {canonical} ({len(text):,} chars)")
        time.sleep(1.0)  # stay polite to the API

    attribution = "\n".join(
        f"- {t} — https://en.wikipedia.org/wiki/{urllib.parse.quote(t.replace(' ', '_'))}"
        for t, _ in articles
    )
    header = (
        "# Virtual Memory: Paging, Address Translation and Related Mechanisms\n\n"
        "Sumber: artikel Wikipedia berbahasa Inggris, dilisensikan CC BY-SA 4.0.\n"
        f"{attribution}\n"
    )

    pages = [header] + [f"# {title}\n\n{text}" for title, text in articles]
    WIKI_OUT.write_text(PAGE_SEPARATOR.join(pages), encoding="utf-8")
    total = sum(len(a[1]) for a in articles)
    print(f"  articles: {len(articles)}  chars: {total:,}")
    return WIKI_OUT


def main() -> int:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    build_law()
    build_os()

    sys.path.insert(0, str(ROOT / "src"))
    from ingestion.chunker import TokenChunker
    from ingestion.parser import DocumentParser

    parser, chunker = DocumentParser(), TokenChunker()
    print("\nCorpus summary")
    print(f"  {'file':<32} {'pages':>6} {'chunks':>7} {'tokens':>8}")
    totals = [0, 0, 0]
    for path in sorted(SAMPLE_DIR.iterdir()):
        if not path.is_file():
            continue
        doc = parser.parse_file(path)
        chunks = chunker.chunk_document(doc)
        tokens = sum(c.metadata.token_count for c in chunks)
        totals = [totals[0] + len(doc.pages), totals[1] + len(chunks), totals[2] + tokens]
        print(f"  {path.name:<32} {len(doc.pages):>6} {len(chunks):>7} {tokens:>8,}")
    print(f"  {'TOTAL':<32} {totals[0]:>6} {totals[1]:>7} {totals[2]:>8,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
