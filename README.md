# Sentinel RAG

[![CI](https://github.com/faizanali-ai/sentinel-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/faizanali-ai/sentinel-rag/actions/workflows/ci.yml)
[![MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-3776ab.svg)](https://www.python.org/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-000000.svg)](https://nextjs.org/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.14_CPU-ee4c2c.svg?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FAISS](https://img.shields.io/badge/FAISS-CPU-blue.svg)](https://github.com/facebookresearch/faiss)
[![Cross-Encoder](https://img.shields.io/badge/Cross--Encoder-MiniLM--L6-orange.svg)](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2)

> "Most RAG systems fail silently. Mine knows when it's failing, fixes itself, and shows you the receipts."

A locally hosted, self-correcting RAG laboratory. Ask a question and watch the answer get routed, retrieved, graded, rewritten with HyDE, and cited — with every step on screen. Three chunking strategies, a hybrid BM25 + FAISS retriever, cross-encoder reranking, and an empirical evaluation harness.

## Screenshots

![Ask — a live run: 3.1 s, grounded answer with footnoted citations](docs/screenshots/ui-trace-success.png)

| Compare — side-by-side and delta | Dark theme |
|---|---|
| ![Compare](docs/screenshots/ui-strategy-delta.png) | ![Ask in dark mode](docs/screenshots/ui-trace-dark.png) |

## Why Sentinel RAG?

| Dimension | Toy / Naive RAG | Sentinel RAG (Production) |
|---|---|---|
| **Chunking** | Arbitrary line counts that chop sentences in half | **3 Evaluated Strategies**: Fixed (512/50), Hierarchical (256/1024), Semantic (Percentile breakpoints) |
| **Retrieval** | Single vector similarity search (misses exact keywords/acronyms) | **Hybrid Search**: BM25 + FAISS fused via Reciprocal Rank Fusion (RRF, $k=60$) |
| **Precision Layer** | Accepts raw top-k vector distances | **Cross-Encoder Reranker** (`ms-marco-MiniLM-L-6-v2`) computing joint query-passage attention |
| **Failure Handling** | Silent hallucinations on low-similarity context | **Self-Correcting Closed Loop**: LLM Grader + HyDE query rewrite + strict citation grounding |
| **Evaluation** | Untested / "Vibe-based" | **Empirical Evaluation Harness**: 16 golden Q&A pairs scoring Precision, Recall, Faithfulness, Relevance |

## What it does

- **Three chunkers, one corpus.** Fixed (512/50), hierarchical (256/1024), and semantic (percentile breakpoints) — switch per query and compare.
- **Hybrid retrieval.** BM25 + FAISS fused with reciprocal rank fusion, so lexical and vector hits both count.
- **Cross-encoder reranking.** Re-scores the top RRF candidates jointly with the query using a transformer cross-encoder (`ms-marco-MiniLM-L-6-v2` / `bge-reranker-base`) for high precision before generation.
- **Self-correction.** An LLM grader scores the retrieved passages; a low score triggers a HyDE rewrite and a re-retrieve, capped at 2 retries.
- **Receipts.** Every step streams to the UI over SSE and is stored in SQLite, with citations that jump to the source chunk.
- **Empirical evaluation harness.** Reference evaluation harness testing 16 curated golden Q&A pairs measuring Context Precision, Context Recall, Faithfulness, and Answer Relevance with latency percentiles.

## Repository Structure

```text
sentinel-rag/
├── backend/
│   ├── app/                 # FastAPI server, chunking strategies, hybrid search, reranker
│   │   ├── chunkers/        # Fixed, Hierarchical (parent-child), and Semantic implementations
│   │   ├── config.py        # Centralized tunable constants
│   │   ├── reranker.py      # Cross-encoder singleton and scoring layer
│   │   ├── retriever.py     # Hybrid BM25 + FAISS retrieval and RRF fusion
│   │   ├── grader.py        # LLM passage relevance judge
│   │   └── pipeline.py      # Step-by-step orchestrator with HyDE self-correction
│   ├── data/                # Golden evaluation dataset (16 pairs) and empirical benchmark results
│   ├── scripts/             # Empirical eval runner and deterministic self-checks
│   └── tests/               # 25 automated pytest tests
├── frontend/
│   ├── app/                 # Next.js 16 App Router (Ask, Compare, Documents)
│   ├── components/          # Real-time SSE trace steps, strategy delta, UI primitives
│   └── hooks/               # Stream consumer with abort/reset guards
├── docs/                    # Screenshots and architecture diagrams
└── README.md
```

## Quickstart

```bash
cd backend
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env          # add GROQ_API_KEY — the free tier is enough for a demo
python scripts/gen_corpus.py  # optional: seed the 50-doc demo corpus (or drop your own .md files in data/corpus/)
python -m app.ingest          # build the indexes for whatever is in data/corpus/
uvicorn app.main:app --port 8000
```

```bash
cd frontend
pnpm install
pnpm dev                      # http://localhost:3000
```

Ask **`What is LoRA?`** — the reliable success demo. The navbar health dot turns amber if the indexes are missing.

<details>
<summary>Full setup: CLI, tests, generated docs</summary>

### CLI

```bash
python -m app.pipeline "How does attention differ from RNN sequence processing?"
python -m app.pipeline "What is LoRA?" --strategy fixed
python -m app.pipeline "What is LoRA?" --no-rerank
python -m app.pipeline "self correction retrieval" --no-correction
python -m app.verify          # query every index, print top hits
python scripts/run_eval.py    # run 6-configuration empirical RAG evaluation
```

### Tests

```bash
cd backend && python -m pytest tests/     # API, documents, retrieval, reranker, eval, ingest, LLM JSON
cd frontend && pnpm test                  # query-stream hook (Vitest)
cd frontend && pnpm lint && pnpm build
```

The backend suite runs deterministic self-checks (`scripts/check_*.py`), mock reranker tests, and evaluation dataset schema validation — no network, no model download. CI runs both suites on every push.

### Generated deliverables (gitignored)

- `make_deck.py` → `Sentinel_RAG.pptx` (15 slides)
- `build_plain_english_guide.py` → `Sentinel_RAG_Comprehensive_Guide.{html,pdf}`

</details>

## How it works

```mermaid
flowchart TD
    A["Corpus (~50 AI/ML docs)"] --> B["Ingestion & Chunking"]
    B --> C1["Fixed 512/50"]
    B --> C2["Hierarchical 256/1024"]
    B --> C3["Semantic (percentile breakpoints)"]
    C1 --> D["bge-small-en-v1.5"]
    C2 --> D
    C3 --> D
    D --> E1["Dense FAISS IndexFlatIP"]
    D --> E2["Sparse BM25 Index"]
    
    Q["User Query"] --> RT["Query Router (Simple vs Complex)"]
    RT --> E1
    RT --> E2
    E1 --> H["Hybrid Retrieval + RRF (k=60)"]
    E2 --> H
    H --> RK["Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)"]
    RK --> G["LLM Grader"]
    G -->|low score| HY["HyDE Rewrite -> Re-retrieve"]
    HY --> RK
    G -->|passed| GEN["Generator (Grounded Answer + Citations)"]

    subgraph Eval["Empirical Evaluation Harness (scripts/run_eval.py)"]
        DS["Golden Dataset (16 Q&A Pairs)"] --> EV["Comparative Benchmark Runner"]
        EV --> M1["Context Precision (MAP)"]
        EV --> M2["Context Recall"]
        EV --> M3["Faithfulness"]
        EV --> M4["Answer Relevance"]
    end
```

A router labels the query simple or complex to pick a retrieval depth. The retriever fuses BM25 and vector hits via Reciprocal Rank Fusion, the Cross-Encoder reranker calculates deep interaction scores to rank the most precise chunks at the top, the grader judges whether the passages can answer the query, and a failure triggers a HyDE rewrite before one more retrieval. The final answer must cite the passages it used; an answer that cites nothing is reported as `not_found` instead of being passed off as grounded.

## Empirical Evaluation Benchmark

Benchmarked using `python scripts/run_eval.py` across 16 golden Q&A pairs spanning 50 AI/ML topics, measuring the full RAG triad and retrieval quality across all 3 chunking strategies, both with and without Cross-Encoder Reranking:

| Strategy | Rerank | Context Precision | Context Recall | Faithfulness | Answer Relevance | Latency p50 | Latency p95 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `fixed` | No | **0.979** | **0.909** | 0.738 | 0.913 | 15.5 ms | 2313.6 ms |
| `fixed` | Yes | **0.958** | **0.911** | 0.750 | 0.909 | 655.3 ms | 1820.7 ms |
| `hierarchical` | No | **0.905** | **0.895** | 0.750 | 0.913 | 15.2 ms | 23.4 ms |
| `hierarchical` | Yes | **0.848** | **0.882** | 0.600 | 0.913 | 305.6 ms | 370.9 ms |
| `semantic` | No | **0.833** | **0.859** | 0.591 | 0.911 | 16.4 ms | 26.4 ms |
| `semantic` | Yes | **0.900** | **0.861** | 0.658 | 0.908 | 277.4 ms | 526.5 ms |

> **Key Architectural Takeaways:**
> - **Reranking Impact**: On semantic chunking, cross-encoder reranking lifts Context Precision from **0.833 to 0.900** (+8.0% relative gain) and Faithfulness from **0.591 to 0.658** (+11.3% relative gain) by prioritizing contextually aligned passages over keyword noise.
> - **Latency Trade-off**: Un-reranked hybrid retrieval achieves ultra-fast p50 retrieval in **~15–16 ms**, while CPU cross-encoder reranking adds predictable ~260–300 ms precision passes.

## Engineering notes

<details>
<summary>Why the code looks the way it does</summary>

- **Atomic index swaps.** A reindex writes to a staging directory and swaps files while holding the retriever lock, so a query can never load a new `.faiss` against an old `chunks.json`. A count tripwire fails loudly if the pair is ever mismatched.
- **Key pooling.** Requests round-robin across `GROQ_API_KEY*` accounts and evict a key on a 401, with the pool guarded by a lock.
- **Cancellation is a trace.** If the client disconnects mid-stream, the server persists a `cancelled` trace with the steps it got instead of losing the run.
- **Untrusted corpus text.** Uploaded passages are delimited and the system prompt says to treat them as data, not instructions. It is mitigation, not a guarantee.
- **Tested where it matters.** The stream hook's abort/reset behavior, the index swap, and the reindex race all have tests.

</details>

## Limits

- Local only — no hosted demo, so it uses your Groq free-tier quota.
- The corpus is synthetic AI/ML text; answers are grounded in whatever you upload.

## License

MIT — see [LICENSE](LICENSE).
