"""CLI script to validate Recall accuracy on the top-25 candidate documents (Phase 2).

Usage:
    python scripts/evaluate_recall.py [--k 25] [--collection zenos_docs]
        [--mode hybrid|dense|sparse] [--show]

This script answers the PRD Phase 2 acceptance criterion:

    *"Validate Recall metric accuracy on the top 25 candidate documents."*

It runs the bundled evaluation set through the chosen retrieval mode and
reports Recall@k per query plus the mean.  ``--mode hybrid`` uses the
database-level RRF fusion search (``QdrantManager.search_hybrid_rrf``).
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import settings
from db.qdrant import QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor
from retrieval.metrics import mean_recall_at_k, recall_at_k

# Make the bundled eval set importable from data/eval/
sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "eval"))

from build_eval_set import build_sample_eval_set  # noqa: E402

console = Console()


def retrieve(mode: str, query: str, extractor: BGEM3EmbeddingExtractor,
             manager: QdrantManager, k: int, collection: str):
    """Run a single query in the requested mode and return chunk ids in order."""
    dense_vec, sparse = extractor.embed_query(query)

    if mode == "dense":
        results = manager.search_dense(
            query_vector=dense_vec, limit=k, collection_name=collection
        )
    elif mode == "sparse":
        results = manager.search_sparse(
            sparse_indices=sparse.indices,
            sparse_values=sparse.values,
            limit=k,
            collection_name=collection,
        )
    else:
        results = manager.search_hybrid_rrf(
            query_vector=dense_vec,
            sparse_indices=sparse.indices,
            sparse_values=sparse.values,
            limit=k,
            collection_name=collection,
        )
    return [r.chunk_id for r in results]


def run_evaluation(mode: str, k: int, collection: str, show: bool):
    manager = QdrantManager()
    extractor = BGEM3EmbeddingExtractor()

    eval_set = build_sample_eval_set()
    relevant_queries = [q for q in eval_set if q["relevant"]]

    console.print(
        Panel.fit(
            f"[bold cyan]Zenos Recall Evaluation (Phase 2)[/bold cyan]\n"
            f"Mode: [magenta]{mode}[/magenta]   "
            f"Top-k: [green]{k}[/green]   "
            f"Collection: [yellow]{collection}[/yellow]   "
            f"Queries: [cyan]{len(relevant_queries)}[/cyan]",
            title="Evaluation Configuration",
        )
    )

    rows = []
    mean_r = 0.0
    total_time = 0.0

    for ev in relevant_queries:
        start = time.perf_counter()
        retrieved = retrieve(mode, ev["query"], extractor, manager, k, collection)
        elapsed = (time.perf_counter() - start) * 1000

        r = recall_at_k(retrieved, ev["relevant"], k=k)
        mean_r += r
        total_time += elapsed

        hits = sum(1 for x in retrieved[:k] if x in set(ev["relevant"]))
        rows.append(
            (
                ev["query"][:70],
                f"{r:.3f}",
                f"{hits}/{len(ev['relevant'])}",
                f"{elapsed:.0f}ms",
            )
        )

        if show:
            console.print(f"\n[bold]Q:[/bold] {ev['query']}")
            console.print(f"[bold]Recall@{k}:[/bold] {r:.3f}  (hits {hits}/{len(ev['relevant'])})")
            for i, cid in enumerate(retrieved[: min(k, 5)], start=1):
                console.print(f"  {i:>2}. [dim]{cid}[/dim]")

    mean_r /= len(relevant_queries)
    avg_ms = total_time / len(relevant_queries)

    table = Table(title=f"Recall@{k} per Query ({mode})")
    table.add_column("Query", style="cyan")
    table.add_column(f"Recall@{k}", justify="right", style="green")
    table.add_column("Hits", justify="center")
    table.add_column("Latency", justify="right", style="yellow")
    for row in rows:
        table.add_row(*row)
    console.print(table)

    console.print(
        f"\n[bold green]Mean Recall@{k}: {mean_r:.3f}[/bold green]  "
        f"(avg latency {avg_ms:.0f} ms/query)"
    )
    return mean_r


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Recall at top-k for Zenos hybrid retrieval")
    parser.add_argument("--k", type=int, default=25, help="Top-k candidates (default 25)")
    parser.add_argument("--collection", type=str, default=None, help="Qdrant collection name")
    parser.add_argument("--mode", type=str, default="hybrid", choices=["hybrid", "dense", "sparse"],
                        help="Retrieval mode to evaluate")
    parser.add_argument("--show", action="store_true", help="Print per-query top results")
    args = parser.parse_args()

    run_evaluation(mode=args.mode, k=args.k, collection=args.collection or settings.qdrant_collection_name, show=args.show)