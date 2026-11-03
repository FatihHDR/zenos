"""CLI for end-to-end Phase 3 Q&A: hybrid retrieval -> rerank -> cited answer.

Usage:
    python scripts/ask.py --query "Apa saja asas Perlindungan Data Pribadi menurut UU PDP?" --show-context
    python scripts/ask.py --interactive
    python scripts/ask.py --query "..." --provider local --json
    python scripts/ask.py --query "..." --stream
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from config import settings
from generation.pipeline import GroundedQAPipeline
from reranking import get_reranker

console = Console()


def build_pipeline(candidates, top_n, provider):
    reranker = get_reranker(provider)
    return GroundedQAPipeline(reranker=reranker, candidates=candidates, top_n=top_n)


def show_context(reranked):
    table = Table(title="Konteks (setelah rerank)")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Score", justify="right", style="green")
    table.add_column("RRF", justify="right", style="yellow")
    table.add_column("chunk_id", style="cyan")
    table.add_column("Cuplikan", style="white")
    for i, r in enumerate(reranked, start=1):
        snippet = (r.text[:80] + "…") if len(r.text) > 80 else r.text
        table.add_row(
            str(i),
            f"{r.score:.4f}",
            f"{r.original_score:.4f}" if r.original_score is not None else "-",
            r.chunk_id,
            snippet,
        )
    console.print(table)


def show_citations(result):
    if result.citations:
        table = Table(title="Sitasi (tervalidasi)")
        table.add_column("Source", style="cyan")
        table.add_column("Pg", justify="right", style="green")
        table.add_column("chunk_id", style="dim")
        for c in result.citations:
            table.add_row(c.source_name, str(c.page_number), c.chunk_id)
        console.print(table)
    else:
        console.print("[dim]Tidak ada sitasi tervalidasi.[/dim]")


def show_answer(result):
    title = "Jawaban (refusal)" if result.refused else "Jawaban"
    style = "yellow" if result.refused else "white"
    console.print(Panel(f"[{style}]{result.answer}[/{style}]", title=title))
    show_citations(result)
    console.print(
        f"[dim]grounded={result.grounded}  refused={result.refused}  "
        f"context={len(result.context_chunk_ids)} chunk[/dim]"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Zenos Phase 3 Q&A: hybrid retrieval + rerank + grounded cited answer"
    )
    parser.add_argument("--query", "-q", type=str, default=None, help="Pertanyaan (kosong = mode interaktif)")
    parser.add_argument("--candidates", type=int, default=None, help="Jumlah kandidat hybrid (default 25)")
    parser.add_argument("--top-n", dest="top_n", type=int, default=None, help="Jumlah chunk setelah rerank (default 5)")
    parser.add_argument("--provider", type=str, default=None, choices=["auto", "cohere", "local"], help="Backend reranker")
    parser.add_argument("--show-context", action="store_true", help="Tampilkan chunk hasil rerank")
    parser.add_argument("--json", action="store_true", help="Cetak hasil sebagai JSON")
    parser.add_argument("--stream", action="store_true", help="Stream jawaban token-demi-token + tampilkan TTFT")
    parser.add_argument("--interactive", action="store_true", help="Mode tanya-jawab berulang")
    args = parser.parse_args()

    pipeline = build_pipeline(args.candidates, args.top_n, args.provider)

    def run_stream(query: str):
        import time

        start = time.perf_counter()
        reranked, stream = pipeline.answer_streaming(query)
        first_token = None
        parts = []
        for delta in stream:
            if first_token is None:
                first_token = time.perf_counter()
            parts.append(delta)
            console.print(delta, end="", soft_wrap=True, highlight=False)
        console.print()
        answer = pipeline.generator.finalize(query, reranked, "".join(parts))
        ttft_ms = ((first_token or time.perf_counter()) - start) * 1000
        if args.show_context:
            show_context(reranked)
        show_citations(answer)
        console.print(
            f"[dim]TTFT {ttft_ms:.0f} ms | grounded={answer.grounded}  "
            f"refused={answer.refused}  context={len(answer.context_chunk_ids)} chunk[/dim]"
        )
        return answer

    def run_one(query: str):
        if args.stream:
            run_stream(query)
            return
        reranked, result = pipeline.answer_with_context(query)
        if args.json:
            console.print_json(data=result.model_dump())
        else:
            if args.show_context:
                show_context(reranked)
            show_answer(result)

    if args.interactive or not args.query:
        console.print(Panel.fit("Zenos Q&A interaktif (Phase 3) — ketik 'exit' untuk keluar", title="Interactive"))
        while True:
            try:
                query = Prompt.ask("[bold cyan]Query[/bold cyan]")
            except (EOFError, KeyboardInterrupt):
                break
            if query.strip().lower() in {"exit", "quit", ":q"}:
                break
            if query.strip():
                run_one(query)
    else:
        run_one(args.query)


if __name__ == "__main__":
    main()
