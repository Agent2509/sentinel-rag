"""Pure eval helpers: trace -> RAGAS sample mapping and score aggregation.

Kept free of any ragas/datasets import so it can be unit-checked in the runtime
venv (scripts/check_eval.py).
"""
import math
from pathlib import Path

METRIC_KEYS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def clean_nan(value):
    """NaN -> None so results are strict JSON (json.dumps emits bare NaN otherwise)."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _contexts(chunks: list[dict]) -> list[str]:
    # Prefer the generator's actual context (parent text for hierarchical).
    return [(c.get("context") or c.get("text") or "") for c in chunks]


def _retrieved_chunks(trace: dict) -> list[dict]:
    # Success -> last retrieval; fallback -> closest_chunks (no generation step).
    steps = trace.get("steps", [])
    generations = [s for s in steps if s.get("action") == "generation"]
    if generations:
        retrievals = [s for s in steps if s.get("action") == "retrieval"]
        return retrievals[-1].get("chunks", []) if retrievals else []
    return trace.get("closest_chunks", [])


def trace_to_sample(trace: dict, row: dict) -> dict:
    """Map a pipeline trace + a testset row to RAGAS SingleTurnSample fields.

    On success: response = generated answer, contexts = last retrieval chunks.
    On fallback: response = fallback message, contexts = closest chunks.
    """
    steps = trace.get("steps", [])
    generations = [s for s in steps if s.get("action") == "generation"]
    chunks = _retrieved_chunks(trace)
    response = (
        generations[0].get("answer", "")
        if generations
        else trace.get("fallback_message", "")
    )

    return {
        "user_input": row["question"],
        "response": response,
        "retrieved_contexts": [c for c in _contexts(chunks) if c],
        "reference": row["reference"],
        "reference_contexts": row.get("reference_contexts", []),
    }


def trace_diagnostics(trace: dict, row: dict) -> dict:
    """Non-metric facts about a run, so a bad run is never mistaken for a result.

    `source_doc_hit` separates "retrieved the wrong doc" from "retrieved the right
    doc but graded/answered wrong"; `grader_error` flags an LLM outage (which the
    pipeline reports as a not_found fallback) rather than a retrieval miss.
    """
    chunks = _retrieved_chunks(trace)
    grades = [
        s.get("grade", {})
        for s in trace.get("steps", [])
        if s.get("action") == "grading"
    ]
    last = grades[-1] if grades else {}
    score = last.get("score")
    target = Path(str(row.get("doc", ""))).stem
    return {
        "final_status": trace.get("final_status"),
        "retries": trace.get("retries", 0),
        "fallback_reason": trace.get("fallback_reason"),
        "grader_score": score,
        "grader_error": bool(last.get("error")) or (bool(grades) and score is None),
        "source_doc_hit": any(
            Path(str(c.get("doc_title") or "")).stem == target for c in chunks
        ),
        "n_contexts": len([c for c in _contexts(chunks) if c]),
    }


def mean_metrics(records: list[dict]) -> dict:
    out: dict = {}
    for key in METRIC_KEYS:
        vals = [
            r[key]
            for r in records
            if isinstance(r.get(key), (int, float)) and r[key] == r[key]  # skips NaN
        ]
        out[key] = round(sum(vals) / len(vals), 4) if vals else None
    return out
