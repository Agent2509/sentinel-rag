"""SQLite (WAL) persistence for traces and eval results.

Connections are opened per call (safe under asyncio.to_thread) and closed via a
context manager. WAL lets trace writes and batch eval writes coexist.
"""
import json
import sqlite3
from contextlib import contextmanager

from app import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS traces (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    query TEXT NOT NULL,
    strategy TEXT NOT NULL,
    correction_enabled INTEGER NOT NULL,
    trace_json TEXT NOT NULL,
    final_status TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    retries INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS eval_results (
    id TEXT PRIMARY KEY,
    strategy TEXT NOT NULL,
    correction_enabled INTEGER NOT NULL,
    question TEXT NOT NULL,
    faithfulness REAL,
    answer_relevancy REAL,
    context_precision REAL,
    context_recall REAL,
    latency_ms INTEGER,
    run_timestamp TEXT NOT NULL,
    corpus_version TEXT
);
"""


@contextmanager
def _connect():
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(eval_results)")}
        if "corpus_version" not in cols:  # older DBs
            conn.execute("ALTER TABLE eval_results ADD COLUMN corpus_version TEXT")


def save_trace(trace: dict) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO traces
              (id, timestamp, query, strategy, correction_enabled, trace_json,
               final_status, latency_ms, retries)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace["trace_id"],
                trace["timestamp"],
                trace["query"],
                trace["strategy"],
                1 if trace.get("correction_enabled") else 0,
                json.dumps(trace),
                trace.get("final_status", ""),
                int(trace.get("total_latency_ms", 0)),
                int(trace.get("retries", 0)),
            ),
        )


def get_trace(trace_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT trace_json FROM traces WHERE id = ?", (trace_id,)
        ).fetchone()
    return json.loads(row["trace_json"]) if row else None


def list_eval_results() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM eval_results ORDER BY run_timestamp"
        ).fetchall()
    return [dict(r) for r in rows]


def count_traces() -> int:
    with _connect() as conn:
        return int(conn.execute("SELECT COUNT(*) AS c FROM traces").fetchone()["c"])


def clear_eval_results() -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM eval_results")


def save_eval_result(row: dict) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO eval_results
              (id, strategy, correction_enabled, question, faithfulness,
               answer_relevancy, context_precision, context_recall,
               latency_ms, run_timestamp, corpus_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["id"],
                row["strategy"],
                1 if row.get("correction_enabled") else 0,
                row["question"],
                row.get("faithfulness"),
                row.get("answer_relevancy"),
                row.get("context_precision"),
                row.get("context_recall"),
                row.get("latency_ms"),
                row["run_timestamp"],
                row.get("corpus_version"),
            ),
        )
