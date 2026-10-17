"""Deterministic API self-check (no LLM, no real model load).

Uses a temp SQLite DB and a faked pipeline so the SSE path and persistence are
exercised end to end without network calls.

    python scripts/check_api.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import config

config.DB_PATH = Path(tempfile.mkdtemp()) / "sentinel_test.db"

from fastapi.testclient import TestClient  # noqa: E402

from app import embeddings, main  # noqa: E402

embeddings.warmup = lambda: None  # do not load the real model in this test


def fake_stream(query, strategy="semantic", correction_enabled=True, trace_id=None):
    tid = trace_id
    yield {
        "type": "step",
        "trace_id": tid,
        "step": {"step_number": 1, "action": "routing", "duration_ms": 5,
                 "result": {"type": "complex", "reason": "t"}},
    }
    yield {
        "type": "step",
        "trace_id": tid,
        "step": {"step_number": 2, "action": "generation", "duration_ms": 5,
                 "answer": "ok [1]",
                 "citations": [{"ref": 1, "chunk_id": "c1", "doc_title": "d.md"}]},
    }
    yield {
        "type": "final",
        "trace_id": tid,
        "trace": {
            "trace_id": tid, "timestamp": "2026-01-01T00:00:00Z", "query": query,
            "strategy": strategy, "correction_enabled": correction_enabled,
            "steps": [], "retries": 0, "final_status": "success", "total_latency_ms": 10,
        },
    }


def main_check() -> None:
    with TestClient(main.app) as client:
        h = client.get("/api/health")
        assert h.status_code == 200, h.text
        assert h.json()["indexes_ok"] is True, h.json()
        print("health           OK  status=", h.json()["status"])

        s = client.get("/api/strategies")
        assert s.status_code == 200 and len(s.json()) == 3
        print("strategies       OK")

        c = client.get("/api/corpus")
        assert c.status_code == 200 and len(c.json()) == 50
        print("corpus           OK  docs=", len(c.json()))

        e = client.get("/api/eval")
        assert e.status_code == 200 and e.json() == []
        print("eval stub        OK")

        assert client.post("/api/query", json={"query": "hi", "strategy": "nope"}).status_code == 400
        assert client.post("/api/query", json={"query": "x" * 3000}).status_code == 400
        print("query validation OK")

        assert client.get("/api/trace/does-not-exist").status_code == 404
        print("trace 404        OK")

        main.pipeline.stream = fake_stream
        r = client.post("/api/query", json={"query": "hello", "strategy": "semantic"})
        assert r.status_code == 200 and "text/event-stream" in r.headers["content-type"], r.headers
        events = [json.loads(line[6:]) for line in r.text.splitlines() if line.startswith("data: ")]
        types = [ev["type"] for ev in events]
        assert types[0] == "start" and types[-1] == "final" and "step" in types, types
        trace_id = events[0]["trace_id"]
        print("SSE stream       OK  events=", types)

        g = client.get(f"/api/trace/{trace_id}")
        assert g.status_code == 200 and g.json()["trace_id"] == trace_id
        print("persistence      OK  trace round-trips")

    print("API self-check PASS")


if __name__ == "__main__":
    main_check()
