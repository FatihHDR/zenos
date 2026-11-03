"""Phase 4: automated Ragas evaluation of the grounded Q&A pipeline.

Maps the PRD's evaluation targets onto concrete metrics:

* **Groundedness** → Ragas ``Faithfulness`` (response vs retrieved context).
* **Answer Relevance** → Ragas ``AnswerRelevancy``.
* **Context Relevance** → context precision computed from the eval set's
  ground-truth chunk ids (deterministic, no reference answer required).

Plus **Recall@k** over the retrieved chunks (PRD success metric: Recall@5 > 90%).
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from retrieval.metrics import recall_at_k

logger = logging.getLogger(__name__)

RAGAS_EVAL_COLUMNS = ("user_input", "response", "retrieved_contexts")


def build_eval_records(
    pipeline: Any,
    eval_set: List[Dict[str, Any]],
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Run ``pipeline`` over ``eval_set`` and collect records for evaluation."""
    records: List[Dict[str, Any]] = []
    for entry in (eval_set[:limit] if limit else eval_set):
        reranked, answer = pipeline.answer_with_context(entry["query"])
        records.append(
            {
                "question": entry["query"],
                "answer": answer.answer,
                "contexts": [c.text for c in reranked],
                "chunk_ids": [c.chunk_id for c in reranked],
                "ground_truth_ids": list(entry.get("relevant", [])),
                "grounded": answer.grounded,
                "refused": answer.refused,
            }
        )
    return records


def compute_recall_at_k(records: List[Dict[str, Any]], k: int = 5) -> float:
    """Mean Recall@k over records that have ground-truth ids (negative controls skipped)."""
    scored = [r for r in records if r["ground_truth_ids"]]
    if not scored:
        return 0.0
    total = sum(
        recall_at_k(r["chunk_ids"], r["ground_truth_ids"], k=k) for r in scored
    )
    return total / len(scored)


def compute_context_relevance(records: List[Dict[str, Any]], k: int = 5) -> float:
    """Mean context precision: fraction of the top-k retrieved chunks that are relevant."""
    scored = [r for r in records if r["ground_truth_ids"]]
    if not scored:
        return 0.0
    total = 0.0
    for r in scored:
        top_k = r["chunk_ids"][:k]
        if not top_k:
            continue
        relevant = set(r["ground_truth_ids"])
        hits = sum(1 for cid in top_k if cid in relevant)
        total += hits / len(top_k)
    return total / len(scored)


def build_ragas_dataset(records: List[Dict[str, Any]]):
    """Build a HuggingFace ``Dataset`` with the columns Ragas expects."""
    from datasets import Dataset

    return Dataset.from_dict(
        {
            "user_input": [r["question"] for r in records],
            "response": [r["answer"] for r in records],
            "retrieved_contexts": [r["contexts"] for r in records],
        }
    )


def _build_judge(model: str, base_url: Optional[str], api_key: Optional[str]):
    """Create a Ragas LLM judge bound to an OpenAI-compatible endpoint."""
    from openai import AsyncOpenAI
    from ragas.llms import llm_factory

    kwargs: Dict[str, Any] = {"api_key": api_key or "sk-9router"}
    if base_url:
        kwargs["base_url"] = base_url
    client = AsyncOpenAI(**kwargs)
    return llm_factory(model, client=client)


def _build_embeddings():
    """Local BGE-M3 embeddings (sentence-transformers) for Ragas metrics."""
    from ragas.embeddings import HuggingFaceEmbeddings

    from config import settings

    return HuggingFaceEmbeddings(model=settings.dense_model_name)


async def _score_all(records: List[Dict[str, Any]], llm: Any, embeddings: Any) -> Dict[str, List[float]]:
    from ragas.metrics.collections import AnswerRelevancy, Faithfulness

    faithfulness = Faithfulness(llm=llm)
    answer_relevancy = AnswerRelevancy(llm=llm, embeddings=embeddings)

    scores: Dict[str, List[float]] = {"groundedness": [], "answer_relevance": []}
    for record in records:
        faith = await faithfulness.ascore(
            user_input=record["question"],
            response=record["answer"],
            retrieved_contexts=record["contexts"],
        )
        relevancy = await answer_relevancy.ascore(
            user_input=record["question"],
            response=record["answer"],
        )
        scores["groundedness"].append(float(faith.value))
        scores["answer_relevance"].append(float(relevancy.value))
    return scores


def run_ragas(
    records: List[Dict[str, Any]],
    judge_model: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    embeddings: Optional[Any] = None,
) -> Dict[str, float]:
    """Evaluate ``records`` with Ragas and return mean scores per metric.

    ``judge_model`` / ``base_url`` / ``api_key`` default to the project's
    OpenAI-compatible configuration (``LLM_MODEL`` / ``OPENAI_BASE_URL`` /
    ``OPENAI_API_KEY``).
    """
    from config import settings

    judge_model = judge_model or settings.llm_model or "auto"
    base_url = base_url or settings.openai_base_url
    api_key = api_key or settings.openai_api_key

    llm = _build_judge(judge_model, base_url, api_key)
    embeddings = embeddings or _build_embeddings()

    per_metric = asyncio.run(_score_all(records, llm, embeddings))
    return {
        name: (sum(values) / len(values) if values else 0.0)
        for name, values in per_metric.items()
    }
