# Phase 4 — Scenarios 1 & 2 (reranked baselines)

Scenarios 1 (dense + cross-encoder) and 2 (sparse + cross-encoder) from PRD Section 5,
run end to end over the same corpus, eval set and reranker settings.

Generated: `2026-11-15T13:35:09Z` · raw results: `results/scenarios-1-2.json`

```bash
python scripts/ingest.py --recreate
python scripts/evaluate_scenarios.py --scenarios 1,2 --out results/scenarios-1-2.json
```

## Configuration

| | |
| --- | --- |
| Corpus | 3 documents, **223 chunks** |
| Collection | `zenos_docs`, 223 points (`dense` 1024-Cosine + `sparse`) |
| Eval set | 8 relevant questions (+1 negative control, excluded — retrieval metrics have no ground truth for it) |
| Candidate pool (k) | 25 |
| Final context (top-n) | 5 |
| Reranker | `LocalCrossEncoderReranker` — `BAAI/bge-reranker-v2-m3`, CPU, fp32 |
| Embeddings | `BAAI/bge-m3` (dense + sparse), CPU |
| Generator | not invoked (metrics here are retrieval-side) |

## Aggregate

| Scenario | Mode | Rerank | Recall@25 | MRR@25 | **Recall@5** | MRR@5 | Retrieval ms | Rerank ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | dense | yes | 1.000 | 0.535 | **0.812** | 0.692 | 2 815 | 67 914 |
| 2 | sparse | yes | 1.000 | 0.596 | **0.812** | 0.688 | 2 310 | 67 867 |

PRD target is **Recall@5 > 90%** → 81.3%, not met but the closest so far.

## Reranker contribution (Scenario 1/2 vs the same mode without reranking)

Compare with `results/phase2-recall.md`, which measured the same two retrieval modes with
**no reranker**. MRR was not implemented in that run, hence "—".

| Configuration | Recall@25 | MRR@25 | Recall@5 | MRR@5 |
| --- | --- | --- | --- | --- |
| dense, no reranker | 1.000 | — | 0.625 | — |
| **dense + reranker (Scenario 1)** | 1.000 | 0.535 | **0.812** | 0.692 |
| sparse, no reranker | 1.000 | — | 0.625 | — |
| **sparse + reranker (Scenario 2)** | 1.000 | 0.596 | **0.812** | 0.688 |

Recall@25 is identical with and without the reranker **by construction** — the reranker
only reorders the same 25 candidates (PRD Section 5). The gain is entirely in Recall@5:
**0.625 → 0.812 (+0.187)** for both modes. This is the largest single improvement measured
in the project so far, and it comes from the component the PRD calls the main quality lever.

## Per question (Recall@5 and MRR@5, after reranking)

| Question | S1 Recall@5 | S1 MRR@5 | S2 Recall@5 | S2 MRR@5 |
| --- | --- | --- | --- | --- |
| Asas Pelindungan Data Pribadi (UU PDP) | 1.000 | 0.333 | 1.000 | 0.250 |
| Definisi Pengendali Data Pribadi | 1.000 | 1.000 | 1.000 | 1.000 |
| Sanksi administratif | 1.000 | 1.000 | 1.000 | 1.000 |
| Manfaat virtual memory | 1.000 | 1.000 | 1.000 | 1.000 |
| TLB hit vs TLB miss | 0.500 | 0.200 | 0.500 | 0.250 |
| Urutan penanganan page fault | **0.000** | 0.000 | **0.000** | 0.000 |
| MMU address translation | 1.000 | 1.000 | 1.000 | 1.000 |
| Page vs page frame | 1.000 | 1.000 | 1.000 | 1.000 |

## Findings

1. **The reranker earns its place.** Recall@5 goes 0.625 → 0.812 in both retrieval modes,
   and the two questions that were worst ranked before (definition of *Pengendali Data
   Pribadi*, rank 1 now; *asas UU PDP*, which failed in every fusion-only mode) are fixed.
   MRR@5 rises to ~0.69, i.e. when the evidence is retrieved it now lands near the top of
   the context instead of anywhere in the pool.
2. **It is not uniformly better.** *"Urutan penanganan page fault"* scored 0.500 with plain
   dense retrieval and scores **0.000** after reranking: the cross-encoder pushed both
   ground-truth chunks out of the top 5. One question regressed while four improved; report
   per-question, because the mean hides the regression.
3. **After reranking, the retrieval mode stops mattering for Recall@5.** Dense and sparse
   both land on 0.812 — different candidate pools (MRR@25 differs: 0.535 vs 0.596), same
   post-rerank quality. Since Recall@25 is 1.000 for both, Scenarios 1 and 2 are already
   saturated at the retrieval stage, which is the same wall Scenario 4 ran into: **the
   comparison that the PRD wants (Scenario 3 vs 1 and 2, i.e. the RRF contribution) has
   little room to show a gain on this corpus** unless Recall@5, not Recall@25, is the
   primary metric.
4. **Latency is the deal-breaker for the local reranker.** Median 73.7 s per query to
   rerank 25 candidates on this CPU (range 55.3–76.3 s), against a PRD TTFT budget of
   **< 2.5 s** — off by roughly 30×. The retrieval stage itself is ~2.3 s here. A local
   fp32 cross-encoder on CPU cannot meet the latency target; either the Cohere Rerank 3 API
   or a GPU is required. (`RERANK_PROVIDER=cohere` needs no code change.)
5. **Recall@25 = 1.000 in every configuration measured so far.** Scenario 1, Scenario 2 and
   the earlier fusion-only runs all saturate. It cannot separate scenarios (PRD Section 7
   suspected this); Recall@5 and MRR are the metrics with signal.

## Caveats

* **Latency numbers are not a valid benchmark.** The host ran out of swap during the
  measurement: swap reached **8191/8191 MiB (100%) within the first minute** and stayed
  pinned, leaving only ~1.5–2.6 GiB of RAM for ~4.5 GB of resident models. Retrieval-only
  latency measured in the earlier standalone run was 220–320 ms warm; here it reads ~2.3 s,
  and the reranker's 73 s/query is inflated by continuous page thrash. Treat both as upper
  bounds and re-measure on a quiet machine (or with `RERANK_PROVIDER=cohere`) before quoting
  them. The *relative* conclusion — a local fp32 cross-encoder on this CPU is orders of
  magnitude too slow for a 2.5 s TTFT budget — holds either way.
  Concrete proof of the pressure: the cluster's Qdrant pod was **`OOMKilled` (exit 137) two
  minutes after the run**. Every query had already been served, so the Recall/MRR numbers
  above are unaffected — but this environment cannot be used as a latency reference.
* **Retrieval-side metrics only.** Groundedness, citation precision, refusal accuracy and
  TTFT are not measured — none of them differ between Scenarios 1 and 2 (same generator,
  same prompt; only the retrieval mode differs), but they are needed for the Scenario 3 vs 4
  comparison.
* **8 questions is a small sample.** Treat gaps below ~0.1 as indicative, not decisive.
* **Ground truth is lexical** (anchor phrases resolved to chunk ids), which is reproducible
  and fail-fast, but coarser than human relevance judgement.
* The negative control contributes nothing here; it is scored by refusal accuracy instead.
