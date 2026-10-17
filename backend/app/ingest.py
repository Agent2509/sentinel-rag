"""Corpus ingestion. `reindex()` rebuilds all strategy indexes atomically-ish:

    python -m app.ingest        (also called by the upload endpoint)

Builds into a staging dir, then swaps files onto the live index, then drops the
in-memory cache. A single-flight lock prevents concurrent rebuilds.
"""
import hashlib
import os
import shutil
import threading

from app import config, retriever
from app.chunkers import fixed, hierarchical, semantic
from app.embeddings import embed_documents
from app.store import save_strategy

CHUNKERS = {
    "fixed": fixed.chunk,
    "hierarchical": hierarchical.chunk,
    "semantic": semantic.chunk,
}

_LOCK = threading.Lock()
_STATE: dict = {"version": None}


def load_corpus() -> list[tuple[str, str]]:
    return [(p.name, p.read_text()) for p in sorted(config.CORPUS_DIR.glob("*.md"))]


def corpus_version() -> str:
    """Stable hash of the normalized corpus (drives eval provenance)."""
    h = hashlib.sha256()
    for path in sorted(config.CORPUS_DIR.glob("*.md")):
        h.update(path.name.encode())
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:16]


def is_running() -> bool:
    return _LOCK.locked()


def version() -> str | None:
    return _STATE["version"]


def reindex(wait: bool = False) -> dict:
    # wait=True queues behind a running rebuild and then re-reads the corpus,
    # so a burst of uploads/deletes converges to the latest file set.
    # ponytail: serialized rebuilds; fine at this size.
    acquired = _LOCK.acquire() if wait else _LOCK.acquire(blocking=False)
    if not acquired:
        raise RuntimeError("reindex already running")
    staging = config.INDEX_DIR / ".staging"
    try:
        docs = load_corpus()
        if not docs:
            raise RuntimeError(f"no documents in {config.CORPUS_DIR}")

        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir(parents=True)
        for name in config.STRATEGIES:
            chunks = []
            for title, text in docs:
                chunks.extend(CHUNKERS[name](text, title))
            for i, c in enumerate(chunks):
                c.chunk_id = f"{name}-{i:04d}"
            vectors = embed_documents([c.text for c in chunks])
            save_strategy(name, chunks, vectors, out_dir=staging)

        # Swap staged files onto the live index under the retriever lock, so a
        # concurrent query can never load a new .faiss against an old
        # chunks.json. Build failures never reach here, so the old index survives.
        # ponytail: per-file os.replace, not globally atomic; `swap_indexes`
        # makes the pair consistent for readers. Use a versioned index dir +
        # pointer file if a crash mid-swap must never mix strategies.
        def apply_swap() -> None:
            for name in config.STRATEGIES:
                for ext in ("faiss", "chunks.json"):
                    os.replace(staging / f"{name}.{ext}", config.INDEX_DIR / f"{name}.{ext}")
                # legacy artifact from the pickle-based store, drop on sight
                (config.INDEX_DIR / f"{name}.bm25.pkl").unlink(missing_ok=True)

        retriever.swap_indexes(apply_swap)
        _STATE["version"] = corpus_version()
        return {"documents": len(docs), "version": _STATE["version"]}
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        _LOCK.release()


def main() -> None:
    info = reindex()
    print(f"Done. {info['documents']} docs indexed, corpus_version={info['version']}")
    print(f"Indexes written to {config.INDEX_DIR}")


if __name__ == "__main__":
    main()
