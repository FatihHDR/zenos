**Product Requirements Document (PRD): Hybrid RAG System & Verified Citations**

**1. Executive Summary**
This search system and AI assistant are designed to process and extract information from complex documents requiring high precision, such as software engineering modules, legal literature, or operating system documentation. Because semantic search often fails to capture specific references, this product combines semantic meaning search with exact keyword search. The final result is verified through a reranker model and bound by a strict citation mechanism to prevent hallucinations.

**2. Tech Stack Recommendations**

| Architescture Component | Primary Choice | Reason for Selection |
| --- | --- | --- |
| **Programming Language** | Python 3.11+ | Industry standard for AI ecosystem engineering and machine learning. |
| **RAG Orchestration** | LlamaIndex | Has the most mature built-in abstractions for executing Hybrid Search, node (metadata) manipulation, and Cross-Encoder reranking. |
| **Vector & Sparse DB** | Qdrant | Supports simultaneous storage of dense vectors and sparse indices (BM25) in a single collection, eliminating the need to maintain two separate databases. |
| **Embedding Model** | `BAAI/bge-m3` | Highly optimal model for generating dense vectors as well as multi-lingual sparse vectors in a single inference. |
| **Reranker Model** | Cohere Rerank 3 API | Highly accurate in providing final relevance scores with low latency. Local/open-source alternative: `BAAI/bge-reranker-v2-m3`. |
| **LLM (Generator)** | Claude 3.5 Sonnet | Proven to have the highest level of system prompt adherence to maintain strict citation formats. |
| **Pipeline Evaluation** | Ragas | Automates the evaluation of RAG Triad metrics using LLM-as-a-Judge. |

**3. Core Feature Specifications**

* **Dual Ingestion Pipeline:** The system will extract text from PDF/Markdown, split it into fixed chunk sizes (e.g., 512 tokens with a 100-token overlap), and inject metadata (`doc_id`, `source_name`, `page_number`). Data is dual-indexed as dense and sparse vectors.
* **Reciprocal Rank Fusion (RRF) Engine:** Upon receiving a query, the system runs parallel searches (semantic and exact). The system will combine the rankings of both results using the RRF algorithm at the database architecture level to normalize score metric differences.
* **Cross-Encoder Reranking:** The pipeline receives the top 25 candidate chunks from the fusion process, processes each (query, chunk) pair through the reranker model, and eliminates the remaining documents to secure the 5 most relevant documents as the final context window.
* **Strict Citation Generation:** The LLM prompt is configured to refuse to answer if the information is not within the provided chunks, and is required to write specific citation tags (e.g., `[Source: Regulation Document A, Pg 14]`) for every declarative sentence generated.

**4. Success Metrics**

* **Retrieval Recall@5 > 90%:** The probability that the document containing the actual answer consistently makes it into the top 5 documents after the reranking process.
* **Groundedness > 95%:** The ratio at which claims made by the LLM can be traced directly back to the source text without the addition of external information.
* **System Latency (TTFT):** The time from the user pressing "Search" until the appearance of the first answer token (Time to First Token) must be under 2.5 seconds.

*Is the target user of this RAG system more focused on internal company document search, or as an interactive feature for the public within an application?*

---

### Phase 1: Infrastructure Setup & Ingestion

* Configure Qdrant DB to accommodate dense and sparse vectors in a single collection.
* Extract and chunk initial datasets (e.g., legal documents from Hukumonline or Operating System literature) with a limit of 512 tokens and a 100-token overlap.
* Execute the `BAAI/bge-m3` model for dual embedding extraction, then inject along with metadata (`doc_id`, page) into the database.

### Phase 2: Hybrid Search & Fusion Implementation

* Build parallel retriever modules using LlamaIndex.
* Apply the Reciprocal Rank Fusion (RRF) algorithm at the database level to combine semantic and exact keyword search results.
* Validate Recall metric accuracy on the top 25 candidate documents.

### Phase 3: Reranking & Grounded Generation

* Integrate Cohere Rerank 3 API to filter the 25 RRF result documents into the 5 chunks with the highest relevance.
* Craft the system prompt on Claude 3.5 Sonnet instructing the LLM to strictly cite source documents using metadata.
* Conduct comprehensive end-to-end Q&A cycle testing.

### Phase 4: Evaluation & Deployment

* Configure automated evaluation using the Ragas framework to monitor Groundedness, Context Relevance, and Answer Relevance metrics.
* Tune parameters to ensure Time to First Token (TTFT) stays under 2.5 seconds.
* Package the LlamaIndex module into an API endpoint (REST/GraphQL) using FastAPI.