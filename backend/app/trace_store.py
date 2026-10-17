"""SQLite (WAL) persistence for traces.

Connections are opened per call (safe under asyncio.to_thread) and closed via a
context manager. WAL keeps trace writes from blocking reads.
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


def list_traces(limit: int = 20) -> list[dict]:
    """Recent trace metadata (no trace_json blob) for the history panel."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, timestamp, query, strategy, correction_enabled,
                   final_status, latency_ms, retries
            FROM traces
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def count_traces() -> int:
    with _connect() as conn:
        return int(conn.execute("SELECT COUNT(*) AS c FROM traces").fetchone()["c"])
