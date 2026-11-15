# Phase 2 — Retrieval recall (fusion only, **no reranker**)

First real numbers produced on the rebuilt corpus. Read the scope note below
before citing these: this is **not** Scenario 1/2/3, because no reranker is used —
the top-5 comes straight from retrieval/fusion (Scenario 4 semantics for hybrid).

## Configuration

| | |
| --- | --- |
| Corpus | 3 documents, **223 chunks** (`data/sample_docs/`, built by `scripts/fetch_corpus.py`) |
| Collection | `zenos_docs` — `dense` (1024, Cosine) + `sparse` named vectors, 223 points |
| Eval set | 8 relevant questions + 1 negative control, ground truth = anchor-resolved chunk ids (11 chunks) |
| Embeddings | `BAAI/bge-m3` (dense + sparse), CPU |
| Reranker | **none** |
| Top-k | 25 (pre-rerank budget) and 5 (final context size) |

```bash
python scripts/ingest.py --recreate
python scripts/evaluate_recall.py --mode {dense,sparse,hybrid} --k {25,5}
```

## Aggregate

| Retrieval mode | Recall@25 | Recall@5 |
| --- | --- | --- |
| dense | 1.000 | 0.625 |
| sparse | 1.000 | 0.625 |
| **hybrid (RRF, k=60)** | 1.000 | **0.688** |

PRD target is **Recall@5 > 90%** — currently **68.8%**. PRD target for Recall@25 was
to discriminate the modes; it does not (see below).

## Per question (Recall@5)

| Question | dense | sparse | hybrid |
| --- | --- | --- | --- |
| Asas Pelindungan Data Pribadi (UU PDP) | 0.000 | 0.000 | 0.000 |
| Definisi Pengendali Data Pribadi | 0.000 | **1.000** | 1.000 |
| Sanksi administratif | 1.000 | 1.000 | 1.000 |
| Manfaat virtual memory | 1.000 | 1.000 | 1.000 |
| TLB hit vs TLB miss | **0.500** | 0.000 | **0.500** |
| Urutan penanganan page fault | **0.500** | 0.000 | 0.000 |
| MMU address translation | 1.000 | 1.000 | 1.000 |
| Page vs page frame | 1.000 | 1.000 | 1.000 |

## Observations

1. **Recall@25 saturates at 1.000 in every mode.** PRD §7 predicted this; it is now
   measured. Recall@25 cannot compare Scenarios 1/2/3 on this corpus — only Recall@5
   (and MRR, not implemented yet) discriminates.
2. **Hybrid helps on the mean but is not a superset.** Mean Recall@5 goes 0.625 →
   0.688 with RRF. However, on *"urutan penanganan page fault"* hybrid scores 0.000
   while dense scores 0.500: the fusion ranked a chunk that dense had found out of the
   top 5. Averaging hides this; report per-question, not just the mean.
3. **The two retrieval signals are complementary, as designed.** Sparse (exact terms)
   wins on *"Pengendali Data Pribadi"* (0.000 → 1.000); dense (semantic) wins on the
   English technical questions (TLB, page fault). This is the qualitative result the
   hybrid design is built on.
4. **One question fails everywhere:** *"Apa saja asas Pelindungan Data Pribadi menurut
   UU PDP?"* scores 0.000 in all three modes — the ground-truth chunk (Pasal 3) never
   reaches the top 5. Worth investigating (the chunk may be dominated by the adjacent
   Pasal 4 list, so the query's embedding drifts).
5. **Latency:** the first query costs ~9.3 s in every mode (cold start — model load plus
   first inference); every subsequent query is **220–320 ms**. Warm retrieval is cheap;
   cold start will dominate TTFT and must be handled separately.
6. **Negative control** is excluded from these numbers (it has no ground truth); its
   behaviour belongs to refusal accuracy, which is not implemented yet.

## What this does not cover

* Scenario 3 (hybrid **with** cross-encoder reranking) — `scripts/evaluate_recall.py` does
  not expose a reranker switch yet.
* MRR, Citation Precision, Refusal Accuracy, Groundedness, TTFT — not implemented.
* 8 questions is a small sample; treat differences below ~0.1 as indicative only.
