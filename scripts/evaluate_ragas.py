"""CLI: automated Ragas evaluation of the Zenos Q&A pipeline (Phase 4, point 1).

Usage:
    python scripts/evaluate_ragas.py [--limit 8] [--k 5] [--judge-model MODEL] [--out results.json]

Reports the PRD evaluation targets: Groundedness (Ragas Faithfulness),
Answer Relevance (Ragas AnswerRelevancy), Context Relevance (context precision),
plus Recall@k — and compares them against the PRD success thresholds.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src and the bundled eval set to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "eval"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import settings
from db.qdrant import QdrantManager
from evaluation import (
    build_eval_records,
    compute_context_relevance,
    compute_recall_at_k,
    run_ragas,
)
from generation.pipeline import GroundedQAPipeline
from build_eval_set import build_sample_eval_set  # noqa: E402

console = Console()

GROUNDEDNESS_TARGET = 0.95
RECALL_TARGET = 0.90


def main():
    parser = argparse.ArgumentParser(description="Ragas evaluation for Zenos grounded Q&A")
    parser.add_argument("--limit", type=int, default=None, help="Evaluate only the first N queries")
    parser.add_argument("--k", type=int, default=5, help="Top-k for Recall@k and context precision")
    parser.add_argument("--judge-model", type=str, default=None, help="LLM judge model (default LLM_MODEL)")
    parser.add_argument("--collection", type=str, default=None, help="Qdrant collection name")
    parser.add_argument("--out", type=str, default=None, help="Write results to a JSON file")
    args = parser.parse_args()

    collection = args.collection or settings.qdrant_collection_name
    manager = QdrantManager()
    points = manager.count_points(collection)
    if points == 0:
        console.print(
            f"[bold red]Collection '{collection}' is empty.[/bold red] "
            "Run `python scripts/setup_db.py --recreate` then "
            "`python scripts/ingest.py --path data/sample_docs` first."
        )
        sys.exit(1)

    eval_set = build_sample_eval_set()
    console.print(
        Panel.fit(
            f"[bold cyan]Zenos Ragas Evaluation (Phase 4)[/bold cyan]\n"
            f"Collection: [yellow]{collection}[/yellow] ({points} points)\n"
            f"Queries: [cyan]{len(eval_set) if not args.limit else min(args.limit, len(eval_set))}[/cyan]   "
            f"k: [green]{args.k}[/green]\n"
            f"Judge: [magenta]{args.judge_model or settings.llm_model}[/magenta] via {settings.openai_base_url}",
            title="Evaluation Configuration",
        )
    )

    pipeline = GroundedQAPipeline()
    records = build_eval_records(pipeline, eval_set, limit=args.limit)

    console.print("[dim]Running Ragas metrics (this calls the judge LLM)...[/dim]")
    ragas_scores = run_ragas(records, judge_model=args.judge_model)

    results = {
        "groundedness": ragas_scores.get("groundedness", 0.0),
        "answer_relevance": ragas_scores.get("answer_relevance", 0.0),
        "context_relevance": compute_context_relevance(records, k=args.k),
        f"recall_at_{args.k}": compute_recall_at_k(records, k=args.k),
        "queries_evaluated": len(records),
    }

    table = Table(title="Evaluation Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Target", justify="right", style="dim")
    table.add_column("Status", justify="center")

    def row(name, value, target=None):
        status = ""
        if target is not None:
            status = "[bold green]PASS[/bold green]" if value >= target else "[bold red]FAIL[/bold red]"
        table.add_row(name, f"{value:.3f}", f"{target:.2f}" if target is not None else "-", status)

    row("Groundedness (Faithfulness)", results["groundedness"], GROUNDEDNESS_TARGET)
    row("Answer Relevance", results["answer_relevance"])
    row("Context Relevance", results["context_relevance"])
    row(f"Recall@{args.k}", results[f"recall_at_{args.k}"], RECALL_TARGET)
    console.print(table)

    if args.out:
        Path(args.out).write_text(json.dumps(results, indent=2))
        console.print(f"[dim]Saved to {args.out}[/dim]")

    return results


if __name__ == "__main__":
    main()
