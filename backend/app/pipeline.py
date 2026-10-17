"""M2/M3 orchestrator: router -> retrieve -> grade -> (HyDE retry) -> generate.

`stream()` is a generator that yields one event per step and then a final trace
event. Every event envelope carries `trace_id`, so the API client always knows it.
This is what M3 pushes over SSE; the CLI here just drains it.
"""
import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone

from app import config, generate, grader, hyde, router
from app.retriever import hybrid_search
from app.store import indexes_exist

_FALLBACK_MESSAGE = (
    "I couldn't find a confident answer in the corpus. "
    "Here are the closest chunks I found:"
)

_TRACE_CHUNK_KEYS = (
    "chunk_id",
    "doc_title",
    "text",
    "parent_id",
    "bm25_rank",
    "vector_rank",
    "rrf_score",
)


def _public(chunks: list[dict]) -> list[dict]:
    # "context" is exactly what the generator read (parent text for hierarchical,
    # child text otherwise), so traces/eval/frontend can verify grounding.
    return [
        {**{k: c.get(k) for k in _TRACE_CHUNK_KEYS}, "context": generate.context_text(c)}
        for c in chunks
    ]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stream(
    query: str,
    strategy: str = "semantic",
    correction_enabled: bool = True,
    trace_id: str | None = None,
):
    if strategy not in config.STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}; expected {config.STRATEGIES}")
    if len(query) > config.MAX_QUERY_CHARS:
        raise ValueError(
            f"query too long ({len(query)} > {config.MAX_QUERY_CHARS} chars)"
        )

    trace: dict = {
        "trace_id": trace_id or str(uuid.uuid4()),
        "timestamp": _now(),
        "query": query,
        "strategy": strategy,
        "correction_enabled": correction_enabled,
        "steps": [],
        "retries": 0,
    }
    tid = trace["trace_id"]
    t0 = time.perf_counter()

    def step_event(action: str, duration_ms: int, **fields) -> dict:
        step = {
            "step_number": len(trace["steps"]) + 1,
            "action": action,
            "duration_ms": duration_ms,
            **fields,
        }
        trace["steps"].append(step)
        return {"type": "step", "trace_id": tid, "step": step}

    def finish(status: str, **extra) -> dict:
        trace["final_status"] = status
        trace["total_latency_ms"] = int(1000 * (time.perf_counter() - t0))
        trace.update(extra)
        return {"type": "final", "trace_id": tid, "trace": trace}

    def fallback(chunks: list[dict], reason: str, **extra) -> dict:
        return finish(
            "not_found",
            fallback_reason=reason,
            fallback_message=_FALLBACK_MESSAGE,
            closest_chunks=_public(chunks),
            **extra,
        )

    # 1. route
    t = time.perf_counter()
    route_result = router.route(query)
    yield step_event(
        "routing", int(1000 * (time.perf_counter() - t)), result=route_result
    )
    is_simple = route_result["type"] == "simple"
    k = config.SIMPLE_TOP_K if is_simple else config.FINAL_TOP_K

    # 2. initial retrieval
    t = time.perf_counter()
    try:
        chunks = hybrid_search(strategy, query, k_final=k)
    except Exception as e:  # noqa: BLE001 - surface as an error trace
        yield finish("error", error=f"retrieval_failed: {type(e).__name__}")
        return
    yield step_event(
        "retrieval",
        int(1000 * (time.perf_counter() - t)),
        query_used=query,
        chunks=_public(chunks),
    )

    # 3. grade, with self-correction loop
    while True:
        t = time.perf_counter()
        g = grader.grade(query, chunks)
        yield step_event(
            "grading",
            int(1000 * (time.perf_counter() - t)),
            grade={
                "relevant": g["relevant"],
                "score": g["score"],
                "reason": g["reason"],
                "error": g["error"],
            },
        )

        grade_ok = (
            not g["error"]
            and g["score"] is not None
            and g["score"] >= config.GRADER_THRESHOLD
        )
        if grade_ok:
            break

        if g["error"]:  # grader failed: fail closed, spend no retries
            yield fallback(chunks, "grader_error")
            return

        if is_simple:
            yield fallback(chunks, "simple_low_score")
            return
        if not correction_enabled:
            yield fallback(chunks, "correction_disabled")
            return
        if trace["retries"] >= config.MAX_RETRIES:
            yield fallback(chunks, "retries_exhausted")
            return

        # HyDE rewrite, then re-retrieve the hypothetical document
        t = time.perf_counter()
        try:
            doc = hyde.rewrite(query)
        except Exception:  # noqa: BLE001 - fall back if the rewrite call fails
            yield fallback(chunks, "hyde_failed")
            return
        if not doc:  # empty rewrite would retrieve garbage; treat as failure
            yield fallback(chunks, "hyde_failed")
            return
        yield step_event(
            "hyde_rewrite",
            int(1000 * (time.perf_counter() - t)),
            hypothetical_document=doc,
        )

        t = time.perf_counter()
        try:
            chunks = hybrid_search(strategy, doc, k_final=config.FINAL_TOP_K, as_query=False)
        except Exception as e:  # noqa: BLE001 - surface as an error trace
            yield finish(
                "error",
                error=f"retrieval_failed: {type(e).__name__}",
                closest_chunks=_public(chunks),
            )
            return
        yield step_event(
            "retrieval",
            int(1000 * (time.perf_counter() - t)),
            query_used="(embedded from hypothetical document)",
            chunks=_public(chunks),
        )
        trace["retries"] += 1

    # 4. generate
    t = time.perf_counter()
    try:
        result = generate.generate(query, chunks)
    except Exception as e:  # noqa: BLE001 - surface as an error trace
        yield finish(
            "error",
            error=f"generation_failed: {type(e).__name__}",
            closest_chunks=_public(chunks),
        )
        return

    # An ungrounded answer (no valid citations) is a failure, not a success.
    # Keep the raw answer so a refusal ("cannot find it") can be told apart from
    # an unparsed citation marker when debugging eval runs.
    if not result["citations"]:
        yield fallback(chunks, "no_citations", raw_answer=result.get("raw", result["answer"]))
        return

    yield step_event(
        "generation",
        int(1000 * (time.perf_counter() - t)),
        answer=result["answer"],
        citations=result["citations"],
    )
    yield finish("success")


def run(
    query: str,
    strategy: str = "semantic",
    correction_enabled: bool = True,
    trace_id: str | None = None,
) -> dict:
    last: dict | None = None
    for event in stream(query, strategy, correction_enabled, trace_id):
        last = event
    if last is None:
        raise RuntimeError("pipeline produced no events")
    return last["trace"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Sentinel RAG pipeline for a single query."
    )
    parser.add_argument("query")
    parser.add_argument("--strategy", default="semantic", choices=config.STRATEGIES)
    parser.add_argument("--no-correction", action="store_true")
    args = parser.parse_args()

    if not indexes_exist():
        sys.exit("Indexes missing. Run: python -m app.ingest")

    try:
        events = stream(args.query, args.strategy, not args.no_correction)
        for event in events:
            if event["type"] == "step":
                s = event["step"]
                print(f"  [{s['step_number']}] {s['action']:<15} {s['duration_ms']:>5} ms")
            else:
                print(json.dumps(event["trace"], indent=2))
                print(f"\nfinal_status: {event['trace']['final_status']}")
    except ValueError as e:
        sys.exit(f"Invalid request: {e}")


if __name__ == "__main__":
    main()
