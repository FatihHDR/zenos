# Zenos API Reference

Zenos adalah sistem **Hybrid RAG** (semantic + keyword search) dengan Qdrant sebagai
vector store. Dokumentasi ini merujuk pada kondisi kode saat ini (**Phase 3**), di mana
belum ada HTTP/REST API — jadi ada dua lapis interface yang tersedia:

1. **Python API** — modul/kelas/fungsi di dalam `src/`.
2. **CLI scripts** — entry point di `scripts/`.

> Phase 4 (FastAPI endpoint + evaluasi Ragas) belum diimplementasikan.

---

## 0. Struktur Paket

```
src/
  config.py                     # Settings (env) -> singleton `settings`
  models.py                     # Pydantic domain models
  db/qdrant.py                  # QdrantManager, HybridSearchResult
  embeddings/bge_m3.py          # BGEM3EmbeddingExtractor, SparseVectorData
  ingestion/parser.py           # DocumentParser
  ingestion/chunker.py          # TokenChunker
  ingestion/pipeline.py         # IngestionPipeline
  retrieval/llama_retrievers.py # DenseRetriever, SparseRetriever, LlamaIndexRRFRetriever
  retrieval/rrf.py              # reciprocal_rank_fusion, rrf_score
  retrieval/metrics.py          # recall_at_k, precision_at_k, mean_recall_at_k, format_recall_report
  reranking/reranker.py         # RerankResult, get_reranker, CohereReranker, LocalCrossEncoderReranker
  generation/prompts.py         # SYSTEM_PROMPT, build_context, extract_citations
  generation/generator.py       # GroundedGenerator (generate + stream)
  generation/pipeline.py        # GroundedQAPipeline
  evaluation/ragas_eval.py      # Ragas Faithfulness/AnswerRelevancy + Recall/context precision
  evaluation/ttft.py            # TTFT measurement
scripts/
  setup_db.py                   # inisialisasi collection
  ingest.py                     # ingest dokumen
  evaluate_recall.py            # evaluasi Recall@k
  ask.py                        # Q&A end-to-end (retrieval -> rerank -> jawaban bersitasi)
  evaluate_ragas.py             # evaluasi otomatis Ragas (Phase 4)
  benchmark_ttft.py             # benchmark TTFT (Phase 4)
```

Semua modul diimpor dengan `src` sebagai root (lihat `pythonpath` di `pyproject.toml`),
mis. `from db.qdrant import QdrantManager`. Script CLI menambahkan `src/` ke `sys.path`
secara manual.

---

## 1. Konfigurasi

`src/config.py` mengekspor singleton `settings` (subclass `pydantic_settings.BaseSettings`),
dimuat dari environment atau file `.env`.

```python
from config import settings
settings.qdrant_host  # "localhost"
```

| Env var | Field | Default | Keterangan |
| --- | --- | --- | --- |
| `QDRANT_HOST` | `qdrant_host` | `localhost` | Host server Qdrant |
| `QDRANT_PORT` | `qdrant_port` | `6333` | REST API |
| `QDRANT_GRPC_PORT` | `qdrant_grpc_port` | `6334` | gRPC API |
| `QDRANT_API_KEY` | `qdrant_api_key` | `None` | API key (opsional) |
| `QDRANT_COLLECTION_NAME` | `qdrant_collection_name` | `zenos_docs` | Nama collection |
| `QDRANT_USE_LOCAL_MEMORY` | `qdrant_use_local_memory` | `False` | `True` = Qdrant in-memory di dalam proses |
| `QDRANT_LOCAL_PATH` | `qdrant_local_path` | `None` | Qdrant embedded berbasis file |
| `DENSE_MODEL_NAME` | `dense_model_name` | `BAAI/bge-m3` | Model dense |
| `SPARSE_MODEL_NAME` | `sparse_model_name` | `BAAI/bge-m3` | Model sparse |
| `DENSE_VECTOR_NAME` | `dense_vector_name` | `dense` | Nama named-vector dense |
| `SPARSE_VECTOR_NAME` | `sparse_vector_name` | `sparse` | Nama named-vector sparse |
| `EMBEDDING_DIMENSION` | `embedding_dimension` | `1024` | Dimensi dense |
| `CHUNK_SIZE` | `chunk_size` | `512` | Ukuran chunk (token) |
| `CHUNK_OVERLAP` | `chunk_overlap` | `100` | Overlap antar chunk (token) |
| `TOKENIZER_NAME` | `tokenizer_name` | `cl100k_base` | Encoder tiktoken |
| `DATA_DIR` | `data_dir` | `./data` | Direktori data |
| `CACHE_DIR` | `cache_dir` | `None` | Cache model embedding |
| `COHERE_API_KEY` | `cohere_api_key` | `None` | API key Cohere Rerank |
| `COHERE_RERANK_MODEL` | `cohere_rerank_model` | `rerank-multilingual-v3.0` | Model Cohere Rerank |
| `RERANK_PROVIDER` | `rerank_provider` | `auto` | `auto` \| `cohere` \| `local` |
| `RERANK_LOCAL_MODEL` | `rerank_local_model` | `BAAI/bge-reranker-v2-m3` | Cross-encoder lokal |
| `RERANK_TOP_N` | `rerank_top_n` | `5` | Jumlah chunk setelah rerank |
| `RETRIEVAL_CANDIDATES` | `retrieval_candidates` | `25` | Kandidat hybrid sebelum rerank |
| `LLM_PROVIDER` | `llm_provider` | `anthropic` | `anthropic` \| `openai` (endpoint OpenAI-compatible: 9router/OpenRouter/Groq/Ollama) |
| `ANTHROPIC_API_KEY` | `anthropic_api_key` | `None` | API key Claude |
| `ANTHROPIC_MODEL` | `anthropic_model` | `claude-3-5-sonnet-latest` | Model generator (provider anthropic) |
| `OPENAI_API_KEY` | `openai_api_key` | `None` | API key endpoint OpenAI-compatible |
| `OPENAI_BASE_URL` | `openai_base_url` | `None` | Base URL (mis. `http://localhost:20128/v1` untuk 9router) |
| `LLM_MODEL` | `llm_model` | `None` | Nama model untuk provider openai (default `auto`) |
| `ANSWER_TEMPERATURE` | `answer_temperature` | `0.0` | Temperature generator |
| `ANSWER_MAX_TOKENS` | `answer_max_tokens` | `1024` | Max token jawaban |

**Mode koneksi Qdrant** (dipilih otomatis di `QdrantManager._init_client`, berurutan):
1. `use_memory=True` → `QdrantClient(location=":memory:")`
2. `local_path` diisi → `QdrantClient(path=...)`
3. selain itu → client remote ke `host:port` dengan `prefer_grpc=True` (**gRPC**)

> Catatan: sejak konfigurasi gRPC diaktifkan, client default memakai gRPC (port `6334`).
> Client juga memakai `timeout=30.0`.

---

## 2. Domain Models (`src/models.py`)

Semua berbasis Pydantic `BaseModel`.

### `DocumentMetadata`
Metadata provenance untuk sitasi.

| Field | Tipe | Default | Keterangan |
| --- | --- | --- | --- |
| `doc_id` | `str` | — | ID dokumen |
| `source_name` | `str` | — | Nama file sumber |
| `page_number` | `int` | `1` | Halaman (1-indexed) |
| `chunk_index` | `int` | `0` | Urutan chunk (0-indexed) |
| `total_chunks` | `int` | `1` | Total chunk dokumen |
| `token_count` | `int` | `0` | Jumlah token chunk |
| `created_at` | `str` | waktu UTC | Timestamp ISO 8601 |
| `extra` | `Dict[str, Any]` | `{}` | Metadata tambahan bebas |

### `DocumentChunk`
Satu unit teks + embedding.

| Field | Tipe | Keterangan |
| --- | --- | --- |
| `chunk_id` | `str` | ID deterministik (`<doc_id>_p<page>_c<chunk>`) |
| `text` | `str` | Isi teks |
| `metadata` | `DocumentMetadata` | Provenance |
| `dense_vector` | `Optional[List[float]]` | Embedding dense (1024-dim) |
| `sparse_indices` | `Optional[List[int]]` | Indeks token sparse |
| `sparse_values` | `Optional[List[float]]` | Bobot sparse |

### `DocumentPage`
- `page_number: int`, `text: str`

### `RawDocument`
Hasil parsing sebelum chunking: `doc_id`, `source_name`, `file_type`, `pages: List[DocumentPage]`.

### `IngestionResult`
Ringkasan ingest: `doc_id`, `source_name`, `num_chunks`, `success`, `error_message`.

### `Citation`
Satu referensi sumber dari jawaban bersitasi: `source_name`, `page_number`, `chunk_id`.

### `GroundedAnswer`
Hasil generate yang terikat ke konteks: `query`, `answer`, `citations: List[Citation]`,
`context_chunk_ids: List[str]`, `grounded: bool`, `refused: bool`.

---

## 3. Python API

### 3.1 Database — `db.qdrant.QdrantManager`

```python
from db.qdrant import QdrantManager

manager = QdrantManager()
```

**`QdrantManager.__init__(host=None, port=None, grpc_port=None, api_key=None, use_memory=None, local_path=None)`**
Semua arg opsional; bila `None` jatuh ke nilai `settings`.

**`init_collection(collection_name=None, dense_vector_name=None, sparse_vector_name=None, dense_dim=None, recreate=False) -> bool`**
Membuat collection dual-vector (`dense` Cosine + `sparse`) beserta payload index pada
`doc_id`, `source_name`, `page_number`, `chunk_index`. `recreate=True` menghapus collection
lama lebih dulu. Return `True`.

**`upsert_chunks(chunks, collection_name=None, dense_vector_name=None, sparse_vector_name=None, batch_size=64) -> int`**
Upsert `List[DocumentChunk]`; ID point = `uuid5(NAMESPACE_DNS, chunk_id)` (idempotent).
Melempar `ValueError` bila ada chunk yang belum punya embedding. Return jumlah point ter-upsert.

**`search_dense(query_vector, limit=25, collection_name=None, vector_name=None, score_threshold=None) -> List[HybridSearchResult]`**
Pencarian semantik murni.

**`search_sparse(sparse_indices, sparse_values, limit=25, collection_name=None, vector_name=None, score_threshold=None) -> List[HybridSearchResult]`**
Pencarian keyword/BM25 murni.

**`search_hybrid_rrf(query_vector, sparse_indices, sparse_values, limit=25, dense_limit=None, sparse_limit=None, collection_name=None, dense_vector_name=None, sparse_vector_name=None, fusion=None, score_threshold=None, with_vectors=False) -> List[HybridSearchResult]`**
Menjalankan dua prefetch paralel (dense + sparse) lalu fusion RRF **di level Qdrant**
(`Fusion.RRF`). `dense_limit`/`sparse_limit` mengatur kandidat per prefetch (default = `limit`).

**`count_points(collection_name=None) -> int`**
Jumlah point; `0` bila collection tidak ada.

**`get_collection_info(collection_name=None) -> Dict[str, Any]`**
Return `{status, points_count, indexed_vectors_count, vectors_config, sparse_vectors_config}`.

**`HybridSearchResult`** (`__slots__`)
Atribut: `chunk_id`, `text`, `score`, `payload`, `dense_score`, `sparse_score`.
Metode `to_dict()` mengembalikan dict `{chunk_id, text, score, dense_score, sparse_score, metadata}`.

---

### 3.2 Embedding — `embeddings.bge_m3`

```python
from embeddings.bge_m3 import BGEM3EmbeddingExtractor

extractor = BGEM3EmbeddingExtractor()
```

**`__init__(model_name=None, dense_model_name=None, sparse_model_name=None, use_fastembed=False, cache_dir=None, device=None)`**
Default `use_fastembed=False` → memakai FlagEmbedding `BGEM3FlagModel`; jika gagal load,
otomatis fallback ke FastEmbed.

**`embed_texts(texts, batch_size=16) -> Tuple[List[List[float]], List[SparseVectorData]]`**
Return `(dense_vectors, sparse_vectors)` untuk daftar teks.

**`embed_chunks(chunks, batch_size=16) -> List[DocumentChunk]`**
Mengisi `dense_vector`, `sparse_indices`, `sparse_values` pada tiap `DocumentChunk` (in-place).

**`embed_query(query) -> Tuple[List[float], SparseVectorData]`**
Vektor dense + sparse untuk satu query.

**`SparseVectorData`** — `indices: List[int]`, `values: List[float]`.

---

### 3.3 Ingestion

#### `ingestion.parser.DocumentParser`

```python
from ingestion.parser import DocumentParser
parser = DocumentParser()
raw = parser.parse_file("data/sample_docs/os_virtual_memory.md")
```

- `compute_doc_id(file_path, content_bytes) -> str` (staticmethod) — `<stem>_<sha256[:16]>`.
- `parse_markdown(path) -> RawDocument` — split page pada delimiter `---page---` bila ada.
- `parse_pdf(path) -> RawDocument` — per halaman; coba PyMuPDF (`fitz`), fallback `pypdf`.
- `parse_text(path) -> RawDocument` — satu halaman.
- `parse_file(path) -> RawDocument` — auto-detect (`.md/.markdown`, `.pdf`, `.txt/.text`; lainnya → text). Melempar `FileNotFoundError` bila tidak ada.

#### `ingestion.chunker.TokenChunker`

```python
from ingestion.chunker import TokenChunker
chunker = TokenChunker()  # 512/100 dari settings
```

- `__init__(chunk_size=None, chunk_overlap=None, tokenizer_name=None)` — melempar
  `ValueError` bila `chunk_overlap >= chunk_size`.
- `count_tokens(text) -> int`
- `chunk_text(text, doc_id, source_name, page_number=1, start_chunk_idx=0) -> List[DocumentChunk]`
- `chunk_document(raw_doc) -> List[DocumentChunk]` — chunk seluruh halaman dan menormalkan
  `total_chunks`.

Format `chunk_id`: `f"{doc_id}_p{page_number}_c{chunk_index}"`.

#### `ingestion.pipeline.IngestionPipeline`

```python
from ingestion.pipeline import IngestionPipeline
pipeline = IngestionPipeline()
res = pipeline.ingest_file("data/sample_docs/os_virtual_memory.md")
```

- `__init__(db_manager=None, embedding_extractor=None, chunker=None, parser=None)` — semua
  default dibuat otomatis.
- `prepare_db(recreate=False) -> None` — inisialisasi collection.
- `ingest_file(file_path, collection_name=None) -> IngestionResult` — parse → chunk → embed → upsert.
- `ingest_directory(directory_path, extensions=None, collection_name=None) -> List[IngestionResult]`
  — rekursif; `extensions` default `[".md", ".pdf", ".txt"]`.

---

### 3.4 Retrieval

#### Retriever LlamaIndex (`retrieval.llama_retrievers`)

Semuanya subclass `llama_index.core.base.base_retriever.BaseRetriever`; pakai `retrieve("query")`
→ `List[NodeWithScore]`.

- **`DenseRetriever(vector_store=None, extractor=None, similarity_top_k=25, filters=None)`** — dense murni.
- **`SparseRetriever(vector_store=None, extractor=None, similarity_top_k=25, filters=None)`** — sparse murni
  (memakai `sparse_query_fn` berbasis BGE-M3).
- **`LlamaIndexRRFRetriever(db_manager=None, extractor=None, similarity_top_k=25, dense_candidates=None, sparse_candidates=None, filters=None)`**
  — facade LlamaIndex di atas `QdrantManager.search_hybrid_rrf` (RRF level DB).

Helper: `sparse_bge_m3_encoder(extractor)` mengembalikan callable `(texts) -> (indices, values)`
untuk `QdrantVectorStore`.

#### RRF (`retrieval.rrf`)

- `DEFAULT_RRF_K = 60`
- `rrf_score(rank, k=60) -> float` — `1 / (k + rank)`; `rank` 1-based.
- `reciprocal_rank_fusion(ranked_lists, k=60, weights=None, key=None) -> List[Tuple[T, float, Dict[int, int]]]`
  — gabungkan banyak ranking; return `(item, fused_score, provenance)` urut skor turun.
  `provenance` memetakan indeks list → rank 1-based.

#### Metrics (`retrieval.metrics`)

- `recall_at_k(retrieved, relevant, k=None) -> float`
- `precision_at_k(retrieved, relevant, k=None) -> float`
- `mean_recall_at_k(evaluations, k) -> float` — rata-rata untuk list dict `{retrieved, relevant}`.
- `format_recall_report(evaluations, k=25) -> str`

---

### 3.5 Reranking (Phase 3) — `reranking.reranker`

Menyaring 25 kandidat RRF menjadi `top_n` (default 5) dengan cross-encoder.

```python
from reranking import get_reranker
reranker = get_reranker()                       # auto: Cohere bila ada key, else lokal
reranked = reranker.rerank("query", candidates, top_n=5)
```

**`RerankResult`** (`__slots__`) — `chunk_id`, `text`, `score` (skor reranker), `original_score`
(skor RRF asal), `payload`; metode `to_dict()`.

**`BaseReranker.rerank(query, results: List[HybridSearchResult], top_n=5) -> List[RerankResult]`** (abstract).
Helper statis `BaseReranker._rank(results, scores, top_n)` melakukan pengurutan (dipakai oleh semua backend, murni & bisa diuji).

**`CohereReranker(api_key=None, model=None, client=None)`** — Cohere Rerank 3 API (`client` bisa di-inject untuk test).
**`LocalCrossEncoderReranker(model_name=None, use_fp16=False, device=None, model=None)`** — cross-encoder lokal `BAAI/bge-reranker-v2-m3` (memerlukan `FlagEmbedding`).

**`get_reranker(provider=None, **kwargs) -> BaseReranker`** — `auto` (default) memilih Cohere bila
`settings.cohere_api_key` ada, kalau tidak → lokal; `cohere`/`local` memaksa backend.

---

### 3.6 Grounded Generation (Phase 3) — `generation`

```python
from generation import GroundedQAPipeline

pipeline = GroundedQAPipeline(candidates=25, top_n=5)
answer = pipeline.answer("Apa saja asas Perlindungan Data Pribadi?")
```

#### `generation.prompts`
- `SYSTEM_PROMPT` — aturan ketat: hanya dari konteks, sitasi tiap kalimat, refuse bila tidak ada.
- `REFUSAL_TEXT` — kalimat penolakan baku.
- `build_context(chunks: List[RerankResult]) -> str` — blok konteks bernomor (source_name, page_number, chunk_id, text).
- `build_user_message(query, context) -> str`
- `extract_citations(answer_text, chunks) -> List[Citation]` — regex `[Source: <name>, Pg <n>]`, hanya yang valid & unik.
- `is_refusal(answer_text) -> bool`

#### `generation.generator.GroundedGenerator`
**`__init__(api_key=None, model=None, temperature=None, max_tokens=None, client=None, provider=None, base_url=None)`**
— `provider` = `anthropic` (default) atau `openai` (endpoint OpenAI-compatible seperti 9router/OpenRouter/Groq/Ollama). `client` bisa di-inject untuk test.
**`generate(query, chunks: List[RerankResult]) -> GroundedAnswer`** — memanggil LLM, memvalidasi sitasi, dan menandai `grounded`/`refused`. Bila `chunks` kosong → langsung refuse tanpa memanggil API.
**`stream(query, chunks: List[RerankResult]) -> Iterator[str]`** — sama seperti `generate` tapi mengalirkan delta token (untuk TTFT / tampilan progresif).
**`finalize(query, chunks, text) -> GroundedAnswer`** — bangun `GroundedAnswer` tervalidasi dari teks yang sudah dihasilkan (dipakai jalur streaming).

#### `generation.pipeline.GroundedQAPipeline`
**`__init__(db_manager=None, extractor=None, reranker=None, generator=None, candidates=None, top_n=None)`**
— default dari `settings`.
- `retrieve(query) -> List[HybridSearchResult]` — hybrid RRF (`search_hybrid_rrf`).
- `answer_with_context(query) -> Tuple[List[RerankResult], GroundedAnswer]`
- `answer(query) -> GroundedAnswer` — retrieve(25) → rerank(5) → generate.
- `answer_streaming(query) -> Tuple[List[RerankResult], Iterator[str]]` — retrieve → rerank → stream delta.

#### `evaluation` (Phase 4)
- `build_eval_records(pipeline, eval_set, limit=None) -> List[dict]`
- `compute_recall_at_k(records, k=5) -> float`
- `compute_context_relevance(records, k=5) -> float`
- `run_ragas(records, judge_model=None, base_url=None, api_key=None) -> Dict[str, float]` — Ragas `Faithfulness` (groundedness) + `AnswerRelevancy`; LLM judge = endpoint OpenAI-compatible (default `.env`), embeddings = BGE-M3 lokal.
- `measure_ttft(pipeline, query) -> dict` / `summarize(rows) -> dict` — TTFT (p50/p95/max).

---

## 4. CLI Scripts

Dijalankan dari root repo (relatif ke `src/` via `sys.path` di dalam script).

### `scripts/setup_db.py`

```bash
python scripts/setup_db.py [--collection NAME] [--recreate] [--memory]
```

| Flag | Keterangan |
| --- | --- |
| `--collection` | Nama collection (default `settings.qdrant_collection_name`) |
| `--recreate` | Hapus lalu buat ulang collection |
| `--memory` | Pakai Qdrant in-memory (tanpa Docker) |

### `scripts/ingest.py`

```bash
python scripts/ingest.py [--path PATH] [--collection NAME] [--recreate] [--memory]
```

| Flag | Keterangan |
| --- | --- |
| `--path`, `-p` | File atau direktori (default `data/sample_docs`) |
| `--collection`, `-c` | Nama collection |
| `--recreate` | Recreate collection sebelum ingest |
| `--memory` | Pakai Qdrant in-memory |

Alur: parse → chunk 512/100 → embed BGE-M3 (dense + sparse) → upsert. Menampilkan tabel ringkasan
jumlah chunk per file + total point.

### `scripts/evaluate_recall.py`

```bash
python scripts/evaluate_recall.py [--k 25] [--collection NAME] [--mode hybrid] [--show]
```

| Flag | Keterangan |
| --- | --- |
| `--k` | Top-k kandidat (default `25`) |
| `--collection` | Nama collection |
| `--mode` | `hybrid` \| `dense` \| `sparse` (default `hybrid`) |
| `--show` | Cetak hasil top per query |

Memakai eval set dari `data/eval/build_eval_set.py` dan mencetak tabel Recall@k per query + mean.

### `scripts/ask.py` (Phase 3)

```bash
python scripts/ask.py --query "Apa saja asas Perlindungan Data Pribadi menurut UU PDP?" --show-context
python scripts/ask.py --interactive
```

| Flag | Keterangan |
| --- | --- |
| `--query`, `-q` | Pertanyaan; bila kosong → mode interaktif |
| `--candidates` | Jumlah kandidat hybrid (default 25) |
| `--top-n` | Jumlah chunk setelah rerank (default 5) |
| `--provider` | `auto` \| `cohere` \| `local` |
| `--show-context` | Tampilkan chunk hasil rerank + skor |
| `--json` | Cetak `GroundedAnswer` sebagai JSON |
| `--stream` | Stream jawaban token-demi-token + tampilkan TTFT |
| `--interactive` | Mode tanya-jawab berulang |

Butuh provider LLM yang aktif (`LLM_PROVIDER` + kredensialnya); `COHERE_API_KEY` opsional (kalau tidak ada → reranker lokal).

### `scripts/evaluate_ragas.py` (Phase 4)

```bash
python scripts/evaluate_ragas.py --limit 8 --k 5
```

Evaluasi otomatis: **Groundedness** (Ragas `Faithfulness`), **Answer Relevance** (Ragas `AnswerRelevancy`),
**Context Relevance** (context precision dari ground-truth eval set), dan **Recall@k** — dibanding ambang PRD.
Flag: `--limit`, `--k`, `--judge-model`, `--collection`, `--out`.

### `scripts/benchmark_ttft.py` (Phase 4)

```bash
python scripts/benchmark_ttft.py --n 3 --candidates 25 --top-n 5
```

Mengukur **TTFT** (retrieve + rerank + token pertama) via streaming, melaporkan p50/p95/max.
Flag: `--n`, `--candidates`, `--top-n`, `--provider`, `--model`, `--out`.

---

## 5. Contoh Programatik

**Ingest satu file:**

```python
from ingestion.pipeline import IngestionPipeline

pipeline = IngestionPipeline()
pipeline.prepare_db(recreate=False)
result = pipeline.ingest_file("data/sample_docs/legal_uu_pdp_2022.md")
print(result.success, result.num_chunks)
```

**Search hybrid (RRF) + lihat top hasil:**

```python
from db.qdrant import QdrantManager
from embeddings.bge_m3 import BGEM3EmbeddingExtractor

manager = QdrantManager()
extractor = BGEM3EmbeddingExtractor()

dense_vec, sparse = extractor.embed_query("Apa itu Translation Lookaside Buffer?")
results = manager.search_hybrid_rrf(
    query_vector=dense_vec,
    sparse_indices=sparse.indices,
    sparse_values=sparse.values,
    limit=25,
)
for r in results[:5]:
    print(r.score, r.chunk_id, r.payload.get("source_name"))
```

**Retriever versi LlamaIndex:**

```python
from retrieval import LlamaIndexRRFRetriever

retriever = LlamaIndexRRFRetriever(similarity_top_k=25)
nodes = retriever.retrieve("Bagaimana urutan penanganan page fault?")
for n in nodes:
    print(n.score, n.node.id_)
```

**Q&A end-to-end bersitasi (Phase 3):**

```python
from generation import GroundedQAPipeline

pipeline = GroundedQAPipeline(candidates=25, top_n=5)
result = pipeline.answer("Apa dasar pemrosesan Data Pribadi?")
print(result.answer)                       # jawaban dengan tag [Source: ..., Pg N]
print(result.grounded, result.refused)     # True False
for c in result.citations:
    print(c.source_name, c.page_number, c.chunk_id)
```

---

## 6. Catatan

- **Urutan wajib**: `setup_db` → `ingest` → baru `evaluate_recall`. Evaluasi sebelum ingest
  akan menghasilkan recall 0 (collection kosong).
- **Mode in-memory bersifat per-proses** — data tidak terbagi antar proses Python, jadi cocok
  hanya untuk pengujian dalam satu proses (mis. `pytest`), bukan alur CLI end-to-end.
- **Reset DB**: `setup_db.py --recreate` atau hapus folder `qdrant_storage`.
- **Dashboard**: `http://localhost:6333/dashboard` (saat Qdrant Docker berjalan).
- **Phase 4**: evaluasi otomatis (Ragas) + benchmark TTFT sudah tersedia di `src/evaluation`,
  `scripts/evaluate_ragas.py`, dan `scripts/benchmark_ttft.py`. Yang **belum**: endpoint FastAPI.
- **Catatan dependency**: `langchain-community` di-pin ke `0.4.1` karena Ragas 0.4.3 masih
  mengimpor `langchain_community.chat_models.vertexai` yang dihapus pada 0.4.2.
- **Provider LLM**: pilih lewat `LLM_PROVIDER`. `anthropic` butuh `ANTHROPIC_API_KEY`.
  `openai` memakai endpoint OpenAI-compatible (`OPENAI_BASE_URL` + `OPENAI_API_KEY` +
  `LLM_MODEL`) — berguna untuk router murah (mis. 9router) atau Ollama lokal.
- **9router & Qdrant di Kubernetes** (kind `kind-k8s-local`, namespace `zenos`): Qdrant
  (StatefulSet+PVC) dan 9router (Deployment `nine-router`+PVC+Secret) diekspos via
  **NodePort** — akses host: `172.20.0.2:30633`/`30634` (Qdrant) dan `172.20.0.2:30128`
  (9router). Manifest di `deploy/k8s/` (lihat README-nya). Catatan: **hostPort tidak bisa
  dipakai** di kernel ini (tanpa `xt_multiport`) → makanya NodePort. Data 9router
  (`~/.9router`) dimigrasi ke PVC.
  **Sumopod** terdaftar sebagai provider custom (`openai-compatible`, prefix `smp`,
  baseUrl `https://ai.sumopod.com/v1`); model Claude-nya `smp/claude-haiku-5-5` dan
  `smp/claude-sonnet-5-5`. Combo `zenos-free` (model free OpenCode `oc/*`) tersedia
  sebagai fallback. Set `.env`: `LLM_PROVIDER=openai`,
  `OPENAI_BASE_URL=http://172.20.0.2:30128/v1`, `OPENAI_API_KEY=<Default Key dashboard>`,
  `LLM_MODEL=smp/claude-haiku-5-5`.
