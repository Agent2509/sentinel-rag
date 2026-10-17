"""Deterministic upload/reindex self-check (no LLM, stubbed embeddings).

    python scripts/check_documents.py
"""
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from app import config  # noqa: E402

_tmp = Path(tempfile.mkdtemp())
config.CORPUS_DIR = _tmp / "corpus"
config.INDEX_DIR = _tmp / "index"
config.DB_PATH = config.INDEX_DIR / "test.db"
config.CORPUS_DIR.mkdir(parents=True)
config.STRATEGIES = ("fixed",)  # skip the embedding-heavy chunkers

from fastapi.testclient import TestClient  # noqa: E402

from app import embeddings, ingest, main, retriever  # noqa: E402

embeddings.warmup = lambda: None  # do not load the real model
ingest.embed_documents = lambda texts, show_progress=False: np.zeros(
    (len(texts), 384), dtype="float32"
)


def wait_idle(prev_version: str | None, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not ingest.is_running() and ingest.version() not in (None, prev_version):
            return
        time.sleep(0.2)
    raise AssertionError("reindex did not finish")


def main_check() -> None:
    (config.CORPUS_DIR / "seed.md").write_text("seed document " * 40)
    ingest.reindex()
    v0 = ingest.version()

    with TestClient(main.app) as client:
        payload = b"Gravity pulls objects toward each other. " * 30
        r = client.post("/api/documents", files={"file": ("notes.txt", payload)})
        assert r.status_code == 200, r.text
        name = r.json()["name"]
        assert r.json()["reindex_started"] is True
        wait_idle(v0)
        print("upload + reindex OK")

        docs = client.get("/api/documents").json()
        assert any(d["name"] == name for d in docs["documents"]), docs
        assert docs["corpus_version"] and docs["reindexing"] is False
        print("list OK")

        retriever.reset_cache()
        hits = retriever.hybrid_search("fixed", "gravity", 3)
        assert any("gravity" in h["text"].lower() for h in hits), hits
        print("retrieval finds uploaded doc OK")

        dup = client.post("/api/documents", files={"file": ("again.txt", payload)})
        assert dup.status_code == 409, dup.status_code
        bad = client.post("/api/documents", files={"file": ("x.csv", b"a,b")})
        assert bad.status_code == 400, bad.status_code
        print("409 duplicate / 400 bad type OK")

        d = client.delete(f"/api/documents/{name}")
        assert d.status_code == 200, d.text
        wait_idle(docs["corpus_version"])
        assert not any(
            x["name"] == name for x in client.get("/api/documents").json()["documents"]
        )
        print("delete + reindex OK")

    print("documents API self-check PASS")


if __name__ == "__main__":
    main_check()
