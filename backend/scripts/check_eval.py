"""Deterministic self-check for the eval harness (no ragas, no LLM).

    python scripts/check_eval.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.build_testset import parse_items
from eval.harness import clean_nan, mean_metrics, trace_diagnostics, trace_to_sample

ROW = {"question": "Q", "reference": "R", "reference_contexts": ["doc"]}


def success_case() -> None:
    trace = {
        "steps": [
            {"action": "retrieval", "chunks": [{"text": "c1"}, {"text": "c2"}]},
            {"action": "generation", "answer": "A [1]", "citations": [{"ref": 1}]},
        ]
    }
    s = trace_to_sample(trace, ROW)
    assert s["user_input"] == "Q"
    assert s["response"] == "A [1]"
    assert s["retrieved_contexts"] == ["c1", "c2"]
    assert s["reference"] == "R"
    assert s["reference_contexts"] == ["doc"]


def fallback_case() -> None:
    trace = {
        "steps": [],
        "final_status": "not_found",
        "fallback_message": "nope",
        "closest_chunks": [{"text": "c9"}],
    }
    s = trace_to_sample(trace, ROW)
    assert s["response"] == "nope"
    assert s["retrieved_contexts"] == ["c9"]


def mean_case() -> None:
    records = [
        {"faithfulness": 0.5, "answer_relevancy": 1.0,
         "context_precision": float("nan"), "context_recall": 0.0},
        {"faithfulness": 0.7, "answer_relevancy": 0.0,
         "context_precision": 0.6, "context_recall": 1.0},
    ]
    m = mean_metrics(records)
    assert m["faithfulness"] == 0.6, m
    assert m["answer_relevancy"] == 0.5, m
    assert m["context_precision"] == 0.6, m  # NaN skipped, not poisoning the mean
    assert m["context_recall"] == 0.5, m
    assert mean_metrics([])["faithfulness"] is None


def clean_nan_case() -> None:
    assert clean_nan(float("nan")) is None
    assert clean_nan(0.5) == 0.5
    assert clean_nan(None) is None
    blob = json.dumps(
        {k: clean_nan(v) for k, v in {"faithfulness": float("nan"), "answer_relevancy": 0.5}.items()}
    )

    def boom(value: str):  # parse_constant fires on bare NaN/Infinity
        raise ValueError(value)

    parsed = json.loads(blob, parse_constant=boom)
    assert parsed == {"faithfulness": None, "answer_relevancy": 0.5}, parsed


def context_case() -> None:
    # generator context must win over the retrieved child text
    trace = {
        "steps": [
            {"action": "retrieval", "chunks": [{"text": "child", "context": "PARENT"}]},
            {"action": "generation", "answer": "A", "citations": [{"ref": 1}]},
        ]
    }
    s = trace_to_sample(trace, ROW)
    assert s["retrieved_contexts"] == ["PARENT"], s["retrieved_contexts"]


def parse_items_case() -> None:
    assert parse_items({"items": [{"question": "q", "answer": "a"}]}, 1) == [
        {"question": "q", "answer": "a"}
    ]
    assert parse_items([], 1) == []          # non-dict response
    assert parse_items({"items": "x"}, 1) == []  # non-list items
    assert parse_items({"items": [{"question": "", "answer": "a"}]}, 1) == []  # empty q
    mixed = parse_items({"items": [None, "junk", {"question": "q", "answer": "a"}]}, 3)
    assert mixed == [{"question": "q", "answer": "a"}], mixed


def diagnostics_case() -> None:
    row = {"question": "Q", "reference": "R", "doc": "activation_functions.md"}
    success = {
        "final_status": "success",
        "retries": 0,
        "steps": [
            {"action": "retrieval", "chunks": [{"doc_title": "activation_functions.md", "text": "c"}]},
            {"action": "grading", "grade": {"score": 0.9, "error": False}},
            {"action": "generation", "answer": "A", "citations": [{"ref": 1}]},
        ],
    }
    d = trace_diagnostics(success, row)
    assert d["final_status"] == "success"
    assert d["grader_score"] == 0.9 and d["grader_error"] is False
    assert d["source_doc_hit"] is True and d["n_contexts"] == 1
    assert d["fallback_reason"] is None

    outage = {
        "final_status": "not_found",
        "retries": 0,
        "fallback_reason": "grader_error",
        "steps": [
            {"action": "retrieval", "chunks": [{"doc_title": "other.md", "text": "c"}]},
            {"action": "grading", "grade": {"score": None, "error": True}},
        ],
        "closest_chunks": [{"doc_title": "other.md", "text": "c"}],
    }
    d = trace_diagnostics(outage, row)
    assert d["fallback_reason"] == "grader_error"
    assert d["grader_error"] is True      # score None is treated as a grader error
    assert d["source_doc_hit"] is False


def main() -> None:
    for case in (
        success_case,
        fallback_case,
        mean_case,
        clean_nan_case,
        context_case,
        parse_items_case,
        diagnostics_case,
    ):
        case()
    print("eval harness self-check PASS (7 cases)")


if __name__ == "__main__":
    main()
