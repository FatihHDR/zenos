"""Generation-side metrics for the PRD scenarios (Section 6, second half).

``scripts/evaluate_scenarios.py`` measures retrieval accuracy (Recall@k, MRR) and never
touches the LLM. This script measures the metrics that require generation:

* **Groundedness** — share of answer claims carrying a validated citation.
* **Citation precision** — share of emitted citation tags pointing at supplied context.
* **Refusal accuracy** — the negative-control question must be refused; a refusal on a
  relevant question is a false refusal and is reported separately.
* **TTFT** — query submission to first answer token (mean, p50, p95), target < 2.5 s.

The negative control is included here (unlike the retrieval script, where it has no ground
truth) because refusing it is precisely what refusal accuracy measures.

Requires **both** Qdrant and the LLM endpoint:

    kubectl -n zenos port-forward svc/qdrant 6333:6333 6334:6334
    kubectl -n zenos port-forward svc/nine-router 20128:20128

Usage:
    python scripts/evaluate_generation.py --scenarios 4 --out results/generation-4.json
    python scripts/evaluate_generation.py --scenarios 3 --out results/generation-3.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "eval"))

from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.table import Table  # noqa: E402

from build_eval_set import build_sample_eval_set  # noqa: E402
from config import settings  # noqa: E402
from db.qdrant import QdrantManager  # noqa: E402
from embeddings.bge_m3 import BGEM3EmbeddingExtractor  # noqa: E402
from evaluation.grounding import evaluate_grounding  # noqa: E402
from evaluation.ttft import measure_ttft_with_context, summarize  # noqa: E402
from generation.pipeline import GroundedQAPipeline  # noqa: E402
from reranking.reranker import get_reranker  # noqa: E402

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
    """Answer every eval question once and score the resulting answers."""
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

    for entry in eval_set:
        query = entry["query"]
        expects_answer = bool(entry["relevant"])

        row, chunks = measure_ttft_with_context(pipeline, query)
        grounding = evaluate_grounding(row["answer"], chunks)

        per_query.append(
            {
                "query": query,
                "expects_answer": expects_answer,
                "refused": row["refused"],
                "grounded": row["grounded"],
                "claims": grounding.claims,
                "cited_claims": grounding.cited_claims,
                "groundedness": round(grounding.groundedness, 4),
                "tags": grounding.tags,
                "valid_tags": grounding.valid_tags,
                "citation_precision": round(grounding.citation_precision, 4),
                "ttft_ms": round(row["ttft_ms"], 1),
                "retrieval_ms": round(row["retrieval_ms"], 1),
                "generation_ms": round(row["generation_ms"], 1),
                "total_ms": round(row["total_ms"], 1),
                "num_contexts": row["num_contexts"],
                "answer": row["answer"],
            }
        )

        if show:
            console.print(f"\n[bold]Scenario {scenario_id}[/bold] | {query}")
            console.print(
                f"  refused={row['refused']} grounded={row['grounded']} "
                f"claims={grounding.cited_claims}/{grounding.claims} "
                f"tags={grounding.valid_tags}/{grounding.tags} "
                f"ttft={row['ttft_ms']:.0f}ms"
            )
            console.print(f"  [dim]{row['answer'][:200]}[/dim]")

    # Groundedness is only defined for answers that actually attempt an answer: a refusal
    # has no claims to trace, and is scored by refusal accuracy instead.
    answered = [r for r in per_query if r["expects_answer"] and not r["refused"]]
    total_claims = sum(r["claims"] for r in answered)
    total_cited = sum(r["cited_claims"] for r in answered)

    all_rows = per_query  # refusals emit no (or no false) tags, so they can be included
    total_tags = sum(r["tags"] for r in all_rows)
    total_valid_tags = sum(r["valid_tags"] for r in all_rows)

    negatives = [r for r in per_query if not r["expects_answer"]]
    refused_negatives = [r for r in negatives if r["refused"]]
    false_refusals = [r for r in per_query if r["expects_answer"] and r["refused"]]

    return {
        "scenario": scenario_id,
        "mode": spec["mode"],
        "rerank": spec["rerank"],
        "purpose": spec["purpose"],
        "metrics": {
            "groundedness": round(total_cited / total_claims, 4) if total_claims else 0.0,
            "citation_precision": (
                round(total_valid_tags / total_tags, 4) if total_tags else 1.0
            ),
            "refusal_accuracy": (
                round(len(refused_negatives) / len(negatives), 4) if negatives else 0.0
            ),
            "false_refusal_rate": (
                round(len(false_refusals) / len(answered + false_refusals), 4)
                if answered or false_refusals
                else 0.0
            ),
        },
        "counts": {
            "questions": len(per_query),
            "answered": len(answered),
            "refusals_on_relevant": len(false_refusals),
            "negative_controls": len(negatives),
            "refused_negative_controls": len(refused_negatives),
            "claims": total_claims,
            "cited_claims": total_cited,
            "tags": total_tags,
            "valid_tags": total_valid_tags,
        },
        "ttft": summarize(per_query),
        "per_query": per_query,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenarios", type=str, default="3,4", help="Comma-separated ids")
    parser.add_argument("--k", type=int, default=None, help="Candidate pool size (default 25)")
    parser.add_argument("--top-n", type=int, default=None, help="Context size (default 5)")
    parser.add_argument("--collection", type=str, default=None, help="Qdrant collection name")
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        choices=["auto", "cohere", "local"],
        help="Reranker backend (default: RERANK_PROVIDER)",
    )
    parser.add_argument("--out", type=str, default=None, help="Write raw results as JSON")
    parser.add_argument("--show", action="store_true", help="Print each answer")
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
    relevant = sum(1 for ev in eval_set if ev["relevant"])

    manager = QdrantManager()
    extractor = BGEM3EmbeddingExtractor()
    needs_reranker = any(SCENARIOS[s]["rerank"] for s in selected)
    reranker = get_reranker(provider=args.provider) if needs_reranker else None
    reranker_label = type(reranker).__name__ if reranker else "none"
    if reranker is not None:
        reranker_label += f" ({getattr(reranker, 'model_name', getattr(reranker, 'model', ''))})"

    llm_label = f"{settings.llm_provider}:{settings.llm_model or settings.anthropic_model}"

    console.print(
        Panel.fit(
            f"[bold cyan]Zenos Generation Evaluation (PRD Section 6)[/bold cyan]\n"
            f"Scenarios: [magenta]{','.join(str(s) for s in selected)}[/magenta]   "
            f"k=[green]{k}[/green]   top_n=[green]{top_n}[/green]\n"
            f"Collection: [yellow]{collection}[/yellow] "
            f"([yellow]{manager.count_points(collection_name=collection)}[/yellow] points)\n"
            f"Reranker: [cyan]{reranker_label}[/cyan]\n"
            f"LLM: [cyan]{llm_label}[/cyan]   "
            f"Queries: [cyan]{len(eval_set)}[/cyan] ({relevant} relevant + "
            f"{len(eval_set) - relevant} negative control)",
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
            eval_set=eval_set,
            k=k,
            top_n=top_n,
            show=args.show,
        )
        results.append(result)

        table = Table(title=f"Scenario {scenario_id}: {spec['mode']} / rerank={spec['rerank']}")
        table.add_column("Query", style="cyan")
        table.add_column("Refused", justify="center")
        table.add_column("Cited/Claims", justify="right")
        table.add_column("Tags ok/all", justify="right")
        table.add_column("TTFT", justify="right", style="yellow")
        for row in result["per_query"]:
            table.add_row(
                row["query"][:40],
                "yes" if row["refused"] else "no",
                f"{row['cited_claims']}/{row['claims']}",
                f"{row['valid_tags']}/{row['tags']}",
                f"{row['ttft_ms']:.0f}ms",
            )
        console.print(table)

    summary = Table(title="Generation summary")
    summary.add_column("Scen", justify="center")
    summary.add_column("Mode", style="magenta")
    summary.add_column("Rerank", justify="center")
    summary.add_column("Groundedness", justify="right", style="green")
    summary.add_column("Cite Precision", justify="right", style="green")
    summary.add_column("Refusal Acc", justify="right")
    summary.add_column("False Refusal", justify="right")
    summary.add_column("TTFT mean", justify="right", style="yellow")
    summary.add_column("TTFT p95", justify="right", style="yellow")
    for result in results:
        m = result["metrics"]
        summary.add_row(
            str(result["scenario"]),
            result["mode"],
            "yes" if result["rerank"] else "no",
            f"{m['groundedness']:.3f}",
            f"{m['citation_precision']:.3f}",
            f"{m['refusal_accuracy']:.3f}",
            f"{m['false_refusal_rate']:.3f}",
            f"{result['ttft']['ttft_mean_ms']:.0f}ms",
            f"{result['ttft']['ttft_p95_ms']:.0f}ms",
        )
    console.print(summary)
    console.print("[dim]PRD targets: groundedness > 0.95, TTFT < 2500 ms[/dim]")

    if args.out:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "collection": collection,
            "collection_points": manager.count_points(collection_name=collection),
            "k": k,
            "top_n": top_n,
            "reranker": reranker_label,
            "llm": llm_label,
            "eval_set": {"relevant": relevant, "negative_controls": len(eval_set) - relevant},
            "scenarios": results,
        }
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        console.print(f"\n[green]Wrote {out_path}[/green]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
