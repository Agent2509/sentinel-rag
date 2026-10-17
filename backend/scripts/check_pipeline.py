"""Deterministic self-check for the pipeline's branchy control flow (no LLM, no

network, no embeddings). Verifies the HyDE retry loop, retry cap, simple-path
fallback, correction toggle, grader-error handling, and HyDE-failure fallback.

    python scripts/check_pipeline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import pipeline

FAKE_CHUNKS = [
    {"chunk_id": "c1", "doc_title": "d.md", "text": "t", "parent_id": None,
     "parent_text": None, "bm25_rank": 0, "vector_rank": 0, "rrf_score": 0.1},
    {"chunk_id": "c2", "doc_title": "d.md", "text": "t2", "parent_id": None,
     "parent_text": None, "bm25_rank": 1, "vector_rank": 1, "rrf_score": 0.05},
]


def _boom(_q):
    raise RuntimeError("hyde failed")


def patch(route_type: str, scores: list, hyde_ok: bool = True) -> None:
    pipeline.router.route = lambda q: {"type": route_type, "reason": "test"}

    sequence = iter(scores)
    state = {"v": scores[-1]}

    def grade(_q, _chunks):
        try:
            state["v"] = next(sequence)
        except StopIteration:
            pass
        v = state["v"]
        if v is None:
            return {"relevant": False, "score": None, "reason": "err", "error": True}
        return {"relevant": v >= 0.6, "score": v, "reason": "t", "error": False}

    pipeline.grader.grade = grade
    pipeline.hyde.rewrite = (lambda q: "hypothetical doc") if hyde_ok else _boom
    pipeline.hybrid_search = lambda *a, **k: FAKE_CHUNKS
    pipeline.generate.generate = lambda q, chunks: {
        "answer": "Answer [1]",
        "citations": [{"ref": 1, "chunk_id": "c1", "doc_title": "d.md"}],
    }


def actions(trace: dict) -> list[str]:
    return [s["action"] for s in trace["steps"]]


def citation_case() -> None:
    # gpt-oss-120b sometimes emits CJK lenticular brackets 【1】 instead of [1];
    # the validator must accept and normalize them, or every such answer is
    # wrongly discarded as ungrounded (no_citations).
    from app.generate import validate_citations

    chunks = [{"chunk_id": "c1", "doc_title": "d.md"}]
    cleaned, cites = validate_citations("Answer【1】 then [2] and [9].", chunks)
    assert cites == [{"ref": 1, "chunk_id": "c1", "doc_title": "d.md"}], cites
    assert "[1]" in cleaned and "【" not in cleaned
    assert "[2]" not in cleaned and "[9]" not in cleaned  # out of range -> dropped
    assert validate_citations("no cites here", chunks) == ("no cites here", [])


def main() -> None:
    citation_case()
    # 1) complex, low then high -> HyDE retry then generate
    patch("complex", [0.3, 0.9])
    t = pipeline.run("q")
    assert t["final_status"] == "success", t["final_status"]
    assert actions(t) == [
        "routing", "retrieval", "grading", "hyde_rewrite", "retrieval", "grading", "generation",
    ], actions(t)
    assert t["retries"] == 1

    # 2) complex, always low -> max retries -> not_found
    patch("complex", [0.3])
    t = pipeline.run("q")
    assert t["final_status"] == "not_found"
    assert t["fallback_reason"] == "retries_exhausted", t.get("fallback_reason")
    assert t["retries"] == 2, t["retries"]
    assert actions(t).count("hyde_rewrite") == 2
    assert t.get("closest_chunks")

    # 3) simple, low -> straight fallback, no HyDE
    patch("simple", [0.1])
    t = pipeline.run("q")
    assert t["final_status"] == "not_found"
    assert t["fallback_reason"] == "simple_low_score", t.get("fallback_reason")
    assert "hyde_rewrite" not in actions(t)

    # 4) complex but correction disabled -> fallback, no HyDE
    patch("complex", [0.1])
    t = pipeline.run("q", correction_enabled=False)
    assert t["final_status"] == "not_found"
    assert t["fallback_reason"] == "correction_disabled", t.get("fallback_reason")
    assert "hyde_rewrite" not in actions(t)

    # 5) grader error -> fail closed, no retries
    patch("complex", [None])
    t = pipeline.run("q")
    assert t["final_status"] == "not_found" and t["retries"] == 0
    assert t["fallback_reason"] == "grader_error", t.get("fallback_reason")
    assert t["steps"][2]["grade"]["error"] is True  # grader error flag is emitted in the trace

    # 6) HyDE failure -> fallback
    patch("complex", [0.3], hyde_ok=False)
    t = pipeline.run("q")
    assert t["final_status"] == "not_found" and "hyde_rewrite" not in actions(t)
    assert t["fallback_reason"] == "hyde_failed", t.get("fallback_reason")

    # 7) grounded answer -> success
    patch("complex", [0.9])
    t = pipeline.run("q")
    assert t["final_status"] == "success" and "generation" in actions(t)
    assert "fallback_reason" not in t

    # 8) ungrounded answer (no valid citations) -> not_found, no generation step
    patch("complex", [0.9])
    pipeline.generate.generate = lambda q, chunks: {"answer": "I cannot find it.", "citations": [], "raw": "I cannot find it."}
    t = pipeline.run("q")
    assert t["final_status"] == "not_found" and "generation" not in actions(t)
    assert t["fallback_reason"] == "no_citations", t.get("fallback_reason")
    assert t["raw_answer"] == "I cannot find it.", t.get("raw_answer")

    print("pipeline self-check PASS (9 cases: citation + 8 control-flow)")


if __name__ == "__main__":
    main()
