"""FastAPI server: SSE query endpoint, trace persistence, health.

    uvicorn app.main:app --port 8000
"""
import asyncio
import json
import threading
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app import config, documents, embeddings, ingest, pipeline, trace_store
from app.chunkers import token_count
from app.store import indexes_exist


def _start_reindex() -> bool:
    """Queue a rebuild in a background thread (serialized behind any running one)."""
    def run() -> None:
        try:
            ingest.reindex(wait=True)
        except Exception as e:  # noqa: BLE001 - background job, log and drop
            print(f"[reindex] failed: {type(e).__name__}: {e}")

    threading.Thread(target=run, daemon=True).start()
    return True

_SENTINEL = object()
_pipeline_sem = asyncio.Semaphore(config.MAX_CONCURRENT_PIPELINES)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    strategy: str = "semantic"
    correction_enabled: bool = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    trace_store.init_db()
    app.state.indexes_ok = indexes_exist()
    if app.state.indexes_ok:
        # Warm the embedder off the event loop; boot returns immediately.
        await asyncio.to_thread(embeddings.warmup)
    else:
        print("[startup] WARNING: indexes missing; run: python -m app.ingest")
    yield


app = FastAPI(title="Sentinel RAG", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _fmt(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


def _advance(gen) -> Any:
    """next() wrapper so StopIteration never crosses an await boundary."""
    try:
        return next(gen)
    except StopIteration:
        return _SENTINEL


async def _sse(req: QueryRequest, request: Request):
    trace_id = str(uuid.uuid4())
    yield _fmt(
        {
            "type": "start",
            "trace_id": trace_id,
            "strategy": req.strategy,
            "correction_enabled": req.correction_enabled,
        }
    )

    final: dict | None = None
    async with _pipeline_sem:
        gen = pipeline.stream(req.query, req.strategy, req.correction_enabled, trace_id)
        try:
            while True:
                event = await asyncio.to_thread(_advance, gen)
                if event is _SENTINEL:
                    break
                if await request.is_disconnected():
                    # stops the loop between steps; an in-flight LLM call cannot be cancelled
                    break
                if event.get("type") == "final":
                    final = event["trace"]
                yield _fmt(event)
        finally:
            gen.close()

    if final is not None:
        await asyncio.to_thread(trace_store.save_trace, final)


@app.post("/api/query")
async def query(req: QueryRequest, request: Request):
    if req.strategy not in config.STRATEGIES:
        raise HTTPException(400, f"unknown strategy {req.strategy!r}")
    if len(req.query) > config.MAX_QUERY_CHARS:
        raise HTTPException(400, f"query exceeds {config.MAX_QUERY_CHARS} characters")
    if not getattr(app.state, "indexes_ok", False):
        raise HTTPException(503, "indexes missing; run: python -m app.ingest")
    return StreamingResponse(_sse(req, request), media_type="text/event-stream")


@app.get("/api/health")
def health():
    return {
        "status": "ok" if getattr(app.state, "indexes_ok", False) else "degraded",
        "indexes_ok": getattr(app.state, "indexes_ok", False),
        "model_ready": embeddings.is_loaded(),
        "corpus_size": len(list(config.CORPUS_DIR.glob("*.md"))),
        "trace_count": trace_store.count_traces(),
        "strategies": list(config.STRATEGIES),
        "reindexing": ingest.is_running(),
        "corpus_version": ingest.version() or ingest.corpus_version(),
    }


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > documents.MAX_BYTES:
        raise HTTPException(413, f"file exceeds {documents.MAX_BYTES} bytes")
    try:
        text = documents.extract_text(file.filename or "upload", data)
        stored = documents.add_document(file.filename or "upload", text)
    except documents.DuplicateDocument as e:
        raise HTTPException(409, f"duplicate of {e}")
    except Exception as e:  # noqa: BLE001 - bad type, unreadable pdf, empty
        raise HTTPException(400, f"could not ingest: {e}")
    return {"name": stored, "reindex_started": _start_reindex()}


@app.get("/api/documents")
def list_documents():
    return {
        "documents": documents.list_documents(),
        "corpus_version": ingest.corpus_version(),
        "reindexing": ingest.is_running(),
    }


@app.delete("/api/documents/{name}")
def delete_document(name: str):
    try:
        documents.remove_document(name)
    except FileNotFoundError:
        raise HTTPException(404, "document not found")
    return {"removed": name, "reindex_started": _start_reindex()}


@app.post("/api/reindex")
def trigger_reindex():
    if ingest.is_running():
        raise HTTPException(409, "reindex already running")
    _start_reindex()
    return {"reindex_started": True}


@app.get("/api/trace/{trace_id}")
def get_trace(trace_id: str):
    trace = trace_store.get_trace(trace_id)
    if trace is None:
        raise HTTPException(404, "trace not found")
    return trace


@app.get("/api/strategies")
def strategies():
    return [
        {
            "name": "fixed",
            "chunk_tokens": config.FIXED_CHUNK_TOKENS,
            "overlap_tokens": config.FIXED_OVERLAP_TOKENS,
        },
        {
            "name": "hierarchical",
            "parent_tokens": config.HIER_PARENT_TOKENS,
            "child_tokens": config.HIER_CHILD_TOKENS,
        },
        {
            "name": "semantic",
            "breakpoint_percentile": config.SEMANTIC_BREAKPOINT_PERCENTILE,
            "max_chunk_tokens": config.SEMANTIC_MAX_CHUNK_TOKENS,
        },
    ]


@app.get("/api/corpus")
def corpus():
    return [
        {"name": path.name, "tokens": token_count(path.read_text())}
        for path in sorted(config.CORPUS_DIR.glob("*.md"))
    ]


@app.get("/api/eval")
def eval_results():
    return trace_store.list_eval_results()


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=config.API_HOST, port=config.API_PORT)


if __name__ == "__main__":
    main()
