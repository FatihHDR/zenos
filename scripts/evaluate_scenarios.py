"""Run the PRD's controlled evaluation scenarios (PRD Section 5).

| Scenario | Retrieval | Reranker       | Purpose              |
| -------- | --------- | -------------- | -------------------- |
| 1        | dense     | cross-encoder  | semantic baseline    |
| 2        | sparse    | cross-encoder  | lexical baseline     |
| 3        | hybrid    | cross-encoder  | full Zenos (main)    |
| 4        | hybrid    | none           | reranker ablation    |

This runner measures the **retrieval** side of each scenario, going through the real
:class:`GroundedQAPipeline` (not a reimplementation) with the scenario's mode and
reranker setting:

* ``Recall@25`` / ``MRR@25`` — the candidate pool, measured *before* reranking so
  Scenarios 1, 2 and 3 can be compared on retrieval alone (PRD Section 6).
* ``Recall@5`` / ``MRR@5`` — the final context handed to the generator, i.e. after the
  reranker, or after fusion when reranking is off (Scenario 4).

Generation metrics (groundedness, citation precision, refusal accuracy, TTFT) are not
measured here; they do not differ between Scenarios 1 and 2.

Usage:
    python scripts/evaluate_scenarios.py --scenarios 1,2
    python scripts/evaluate_scenarios.py --out results/scenarios.json
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "eval"))

from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.table import Table  # noqa: E402

from build_eval_set import build_sample_eval_set  # noqa: E402
from config import settings  # noqa: E402
from db.qdrant import QdrantManager  # noqa: E402
from embeddings.bge_m3 import BGEM3EmbeddingExtractor  # noqa: E402
from generation.pipeline import GroundedQAPipeline  # noqa: E402
from reranking.reranker import get_reranker  # noqa: E402
from retrieval.metrics import (  # noqa: E402
    mean_recall_at_k,
    mean_reciprocal_rank,
    recall_at_k,
    reciprocal_rank,
)

console = Console()

SCENARIOS: Dict[int, Dict[str, Any]] = {
    1: {"mode": "dense", "rerank": True, "purpose": "Semantic baseline"},
    2: {"mode": "sparse", "rerank": True, "purpose": "Lexical baseline"},
    3: {"mode": "hybrid", "rerank": True, "purpose": "Main model (full Zenos)"},
    4: {"mode": "hybrid", "rerank": False, "purpose": "Ablation: reranker off"},
}


def run_scenario(
    scenario_id: int,
    spec: Dict[str, Any],
    *,
    extractor: BGEM3EmbeddingExtractor,
    manager: QdrantManager,
    reranker: Any,
    eval_set: List[Dict[str, Any]],
    k: int,
    top_n: int,
    show: bool,
) -> Dict[str, Any]:
    """Run one scenario over the eval set and return its metrics."""
    pipeline = GroundedQAPipeline(
        db_manager=manager,
        extractor=extractor,
        reranker=reranker if spec["rerank"] else None,
        retrieval_mode=spec["mode"],
        rerank=spec["rerank"],
        candidates=k,
        top_n=top_n,
    )

    per_query: List[Dict[str, Any]] = []
    pool_rows: List[Dict[str, Any]] = []
    context_rows: List[Dict[str, Any]] = []

    for entry in eval_set:
        query = entry["query"]
        relevant = entry["relevant"]

        started = time.perf_counter()
        candidates = pipeline.retrieve(query)
        retrieval_ms = (time.perf_counter() - started) * 1000

        started = time.perf_counter()
        context = pipeline.select_context(query, candidates)
        select_ms = (time.perf_counter() - started) * 1000

        retrieved_ids = [c.chunk_id for c in candidates]
        context_ids = [c.chunk_id for c in context]

        pool_rows.append({"retrieved": retrieved_ids, "relevant": relevant})
        context_rows.append({"retrieved": context_ids, "relevant": relevant})
        per_query.append(
            {
                "query": query,
                f"retrieved@{k}": retrieved_ids,
                f"context@{top_n}": context_ids,
                "retrieval_ms": round(retrieval_ms, 1),
                "select_ms": round(select_ms, 1),
            }
        )

        if show:
            console.print(f"\n[bold]Scenario {scenario_id}[/bold] | {query}")
            console.print(f"  pool@{k}: {retrieved_ids[:5]}")
            console.print(f"  context@{top_n}: {context_ids}")

    totals = [q["retrieval_ms"] + q["select_ms"] for q in per_query]
    return {
        "scenario": scenario_id,
        "mode": spec["mode"],
        "rerank": spec["rerank"],
        "purpose": spec["purpose"],
        "metrics": {
            f"recall@{k}": round(mean_recall_at_k(pool_rows, k), 4),
            f"mrr@{k}": round(mean_reciprocal_rank(pool_rows, k), 4),
            f"recall@{top_n}": round(mean_recall_at_k(context_rows, top_n), 4),
            f"mrr@{top_n}": round(mean_reciprocal_rank(context_rows, top_n), 4),
        },
        "latency_ms": {
            "retrieval_mean": round(sum(q["retrieval_ms"] for q in per_query) / len(per_query), 1),
            "select_mean": round(sum(q["select_ms"] for q in per_query) / len(per_query), 1),
            "total_mean": round(sum(totals) / len(totals), 1),
            "total_max": round(max(totals), 1),
        },
        "per_query": per_query,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--scenarios",
        type=str,
        default=",".join(str(s) for s in SCENARIOS),
        help="Comma-separated scenario ids (default: all)",
    )
    parser.add_argument("--k", type=int, default=None, help="Candidate pool size (default 25)")
    parser.add_argument("--top-n", type=int, default=None, help="Final context size (default 5)")
    parser.add_argument("--collection", type=str, default=None, help="Qdrant collection name")
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["auto", "cohere", "local"],
        help="Reranker backend (default: RERANK_PROVIDER)",
    )
    parser.add_argument("--out", type=str, default=None, help="Write raw results as JSON")
    parser.add_argument("--show", action="store_true", help="Print per-query rankings")
    args = parser.parse_args()

    try:
        selected = [int(part) for part in args.scenarios.split(",") if part.strip()]
    except ValueError:
        console.print(f"[red]--scenarios must be comma-separated integers, got {args.scenarios!r}[/red]")
        return 2
    unknown = [s for s in selected if s not in SCENARIOS]
    if unknown:
        console.print(f"[red]Unknown scenario id(s) {unknown}. Known: {sorted(SCENARIOS)}[/red]")
        return 2

    k = args.k or settings.retrieval_candidates
    top_n = args.top_n or settings.rerank_top_n
    collection = args.collection or settings.qdrant_collection_name

    eval_set = build_sample_eval_set()
    relevant_queries = [ev for ev in eval_set if ev["relevant"]]
    negatives = len(eval_set) - len(relevant_queries)

    manager = QdrantManager()
    extractor = BGEM3EmbeddingExtractor()
    needs_reranker = any(SCENARIOS[s]["rerank"] for s in selected)
    reranker = get_reranker(provider=args.provider) if needs_reranker else None
    reranker_label = type(reranker).__name__ if reranker else "none"
    if reranker is not None:
        reranker_label += f" ({getattr(reranker, 'model_name', getattr(reranker, 'model', ''))})"

    console.print(
        Panel.fit(
            f"[bold cyan]Zenos Scenario Evaluation (PRD Section 5)[/bold cyan]\n"
            f"Scenarios: [magenta]{','.join(str(s) for s in selected)}[/magenta]   "
            f"k=[green]{k}[/green]   top_n=[green]{top_n}[/green]\n"
            f"Collection: [yellow]{collection}[/yellow] "
            f"([yellow]{manager.count_points(collection_name=collection)}[/yellow] points)   "
            f"Reranker: [cyan]{reranker_label}[/cyan]\n"
            f"Queries: [cyan]{len(relevant_queries)}[/cyan] relevant "
            f"(+{negatives} negative control, excluded from retrieval metrics)",
            title="Evaluation Configuration",
        )
    )

    results: List[Dict[str, Any]] = []
    for scenario_id in selected:
        spec = SCENARIOS[scenario_id]
        console.print(
            f"\n[bold]Scenario {scenario_id}[/bold] — {spec['mode']} "
            f"+ {'reranker' if spec['rerank'] else 'no reranker'} ({spec['purpose']})"
        )
        result = run_scenario(
            scenario_id,
            spec,
            extractor=extractor,
            manager=manager,
            reranker=reranker,
            eval_set=relevant_queries,
            k=k,
            top_n=top_n,
            show=args.show,
        )
        results.append(result)

        table = Table(title=f"Scenario {scenario_id}: {spec['mode']} / rerank={spec['rerank']}")
        table.add_column("Query", style="cyan")
        table.add_column(f"Recall@{k}", justify="right")
        table.add_column(f"MRR@{k}", justify="right")
        table.add_column(f"Recall@{top_n}", justify="right", style="green")
        table.add_column(f"MRR@{top_n}", justify="right", style="green")
        for query_row, entry in zip(result["per_query"], relevant_queries):
            relevant = entry["relevant"]
            pool = query_row[f"retrieved@{k}"]
            context = query_row[f"context@{top_n}"]
            table.add_row(
                entry["query"][:48],
                f"{recall_at_k(pool, relevant, k=k):.3f}",
                f"{reciprocal_rank(pool, relevant, k=k):.3f}",
                f"{recall_at_k(context, relevant, k=top_n):.3f}",
                f"{reciprocal_rank(context, relevant, k=top_n):.3f}",
            )
        console.print(table)

    summary = Table(title="Scenario summary")
    summary.add_column("Scenario", justify="center")
    summary.add_column("Mode", style="magenta")
    summary.add_column("Rerank", justify="center")
    summary.add_column(f"Recall@{k}", justify="right")
    summary.add_column(f"MRR@{k}", justify="right")
    summary.add_column(f"Recall@{top_n}", justify="right", style="green")
    summary.add_column(f"MRR@{top_n}", justify="right", style="green")
    summary.add_column("Retrieval ms", justify="right", style="yellow")
    summary.add_column("Rerank ms", justify="right", style="yellow")
    for result in results:
        metrics = result["metrics"]
        summary.add_row(
            str(result["scenario"]),
            result["mode"],
            "yes" if result["rerank"] else "no",
            f"{metrics[f'recall@{k}']:.3f}",
            f"{metrics[f'mrr@{k}']:.3f}",
            f"{metrics[f'recall@{top_n}']:.3f}",
            f"{metrics[f'mrr@{top_n}']:.3f}",
            f"{result['latency_ms']['retrieval_mean']:.0f}",
            f"{result['latency_ms']['select_mean']:.0f}",
        )
    console.print(summary)

    if args.out:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "collection": collection,
            "collection_points": manager.count_points(collection_name=collection),
            "k": k,
            "top_n": top_n,
            "reranker": reranker_label,
            "eval_set": {"relevant": len(relevant_queries), "negative_controls": negatives},
            "scenarios": results,
        }
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"\n[green]Wrote {out_path}[/green]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
