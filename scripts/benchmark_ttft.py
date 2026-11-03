"""CLI: benchmark time-to-first-token (TTFT) for the Zenos Q&A pipeline (Phase 4, point 2).

Usage:
    python scripts/benchmark_ttft.py [--n 3] [--candidates 25] [--top-n 5]
        [--provider auto|cohere|local] [--model MODEL] [--out results.json]

Measures TTFT (retrieve + rerank + first answer token) across the bundled eval
queries and prints p50/p95/max. Use it to tune toward the PRD target of < 2.5s.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "eval"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import settings
from db.qdrant import QdrantManager
from evaluation import measure_ttft, summarize
from generation.pipeline import GroundedQAPipeline
from reranking import get_reranker
from build_eval_set import build_sample_eval_set  # noqa: E402

console = Console()

TTFT_TARGET_MS = 2500.0


def main():
    parser = argparse.ArgumentParser(description="TTFT benchmark for Zenos grounded Q&A")
    parser.add_argument("--n", type=int, default=3, help="Repetitions per query")
    parser.add_argument("--candidates", type=int, default=None, help="Hybrid retrieval candidate pool")
    parser.add_argument("--top-n", dest="top_n", type=int, default=None, help="Chunks after rerank")
    parser.add_argument("--provider", type=str, default=None, choices=["auto", "cohere", "local"])
    parser.add_argument("--model", type=str, default=None, help="Generator model override")
    parser.add_argument("--collection", type=str, default=None, help="Qdrant collection name")
    parser.add_argument("--out", type=str, default=None, help="Write results to a JSON file")
    args = parser.parse_args()

    collection = args.collection or settings.qdrant_collection_name
    if QdrantManager().count_points(collection) == 0:
        console.print(
            f"[bold red]Collection '{collection}' is empty.[/bold red] Ingest documents first "
            "(`setup_db.py --recreate` + `ingest.py --path data/sample_docs`)."
        )
        sys.exit(1)

    reranker = get_reranker(args.provider)
    generator = None
    if args.model:
        from generation.generator import GroundedGenerator

        generator = GroundedGenerator(model=args.model)

    pipeline = GroundedQAPipeline(
        reranker=reranker,
        generator=generator,
        candidates=args.candidates,
        top_n=args.top_n,
    )

    queries = [ev["query"] for ev in build_sample_eval_set() if ev.get("relevant")] or [
        ev["query"] for ev in build_sample_eval_set()
    ]

    console.print(
        Panel.fit(
            f"[bold cyan]Zenos TTFT Benchmark (Phase 4)[/bold cyan]\n"
            f"Queries: [cyan]{len(queries)}[/cyan] × [cyan]{args.n}[/cyan] reps\n"
            f"Reranker: [magenta]{type(reranker).__name__}[/magenta]   "
            f"Candidates: [green]{pipeline.candidates}[/green]   Top-n: [green]{pipeline.top_n}[/green]\n"
            f"Model: [yellow]{pipeline.generator.model}[/yellow]   Target: < {TTFT_TARGET_MS:.0f} ms",
            title="Benchmark Configuration",
        )
    )

    rows = []
    for _ in range(args.n):
        for query in queries:
            row = measure_ttft(pipeline, query)
            rows.append(row)
            console.print(
                f"  [dim]ttft[/dim] {row['ttft_ms']:7.0f} ms "
                f"| [dim]retr[/dim] {row['retrieval_ms']:7.0f} ms "
                f"| [dim]total[/dim] {row['total_ms']:7.0f} ms "
                f"| grounded={row['grounded']}  {query[:50]}"
            )

    stats = summarize(rows)

    table = Table(title="TTFT Summary")
    table.add_column("Stat", style="cyan")
    table.add_column("Value", justify="right", style="green")
    for key in ("count", "ttft_p50_ms", "ttft_p95_ms", "ttft_max_ms", "ttft_mean_ms", "retrieval_mean_ms"):
        value = stats[key]
        table.add_row(key, f"{value:.0f}" if key != "count" else str(int(value)))
    console.print(table)

    verdict = "[bold green]PASS[/bold green]" if stats["ttft_p95_ms"] < TTFT_TARGET_MS else "[bold red]FAIL[/bold red]"
    console.print(
        f"p95 TTFT {stats['ttft_p95_ms']:.0f} ms vs target < {TTFT_TARGET_MS:.0f} ms → {verdict}"
    )

    if args.out:
        Path(args.out).write_text(json.dumps({"stats": stats, "rows": rows}, indent=2))
        console.print(f"[dim]Saved to {args.out}[/dim]")

    return stats


if __name__ == "__main__":
    main()
