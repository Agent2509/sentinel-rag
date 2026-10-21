"""Unit tests for the RAGAS evaluation harness and golden dataset."""
import json
from pathlib import Path
import pytest

from scripts.run_eval import (
    EVAL_DATASET_PATH,
    compute_context_precision,
    compute_context_recall,
    compute_answer_relevance_semantic,
    compute_faithfulness_heuristic,
    format_markdown_table,
    load_eval_dataset,
)


def test_eval_dataset_schema_and_integrity():
    assert EVAL_DATASET_PATH.exists(), "eval_dataset.json must exist"
    dataset = load_eval_dataset()
    assert len(dataset) >= 15, f"Expected at least 15 items, found {len(dataset)}"

    corpus_dir = EVAL_DATASET_PATH.parent / "corpus"
    for item in dataset:
        assert "id" in item and item["id"]
        assert "query" in item and len(item["query"]) > 10
        assert "ground_truth" in item and len(item["ground_truth"]) > 15
        assert "doc_title" in item and item["doc_title"].endswith(".md")
        doc_path = corpus_dir / item["doc_title"]
        assert doc_path.exists(), f"Corpus file {doc_path} referenced in dataset does not exist"


def test_context_precision_calculation():
    # Target doc at rank 1 (out of 3)
    chunks_top = [
        {"doc_title": "lora_and_peft.md"},
        {"doc_title": "linear_algebra.md"},
        {"doc_title": "decision_trees.md"},
    ]
    p1 = compute_context_precision("lora_and_peft.md", chunks_top)
    assert p1 == pytest.approx(1.0)

    # Target doc at rank 2
    chunks_second = [
        {"doc_title": "linear_algebra.md"},
        {"doc_title": "lora_and_peft.md"},
    ]
    p2 = compute_context_precision("lora_and_peft.md", chunks_second)
    assert p2 == pytest.approx(0.5)

    # Target doc missing
    p_none = compute_context_precision("missing.md", chunks_top)
    assert p_none == 0.0

    # Empty list
    assert compute_context_precision("any.md", []) == 0.0


def test_context_recall_calculation():
    chunks = [
        {"doc_title": "lora_and_peft.md", "text": "LoRA freezes weights and injects low-rank matrices"},
    ]
    gt = "LoRA freezes model weights and adds low-rank adaptation matrices to reduce memory."
    recall = compute_context_recall("lora_and_peft.md", gt, chunks)
    assert recall > 0.7

    # Target doc not retrieved
    unrelated_chunks = [{"doc_title": "unrelated.md", "text": "something completely different"}]
    zero_recall = compute_context_recall("lora_and_peft.md", gt, unrelated_chunks)
    assert zero_recall < 0.2


def test_faithfulness_heuristic():
    chunks = [{"doc_title": "test.md", "text": "Attention weights are computed using queries and keys."}]
    answer_cited = "Attention weights depend on queries and keys [1]."
    f_cited = compute_faithfulness_heuristic(answer_cited, chunks)
    assert f_cited > 0.5

    answer_uncited = "Attention weights depend on queries and keys."
    f_uncited = compute_faithfulness_heuristic(answer_uncited, chunks)
    assert f_uncited <= 0.2


def test_format_markdown_table():
    sample_results = [
        {
            "strategy": "fixed",
            "rerank": False,
            "mean_context_precision": 0.75,
            "mean_context_recall": 0.80,
            "mean_faithfulness": 0.85,
            "mean_answer_relevance": 0.82,
            "latency_p50_ms": 120.0,
            "latency_p95_ms": 250.0,
        },
        {
            "strategy": "fixed",
            "rerank": True,
            "mean_context_precision": 0.92,
            "mean_context_recall": 0.88,
            "mean_faithfulness": 0.91,
            "mean_answer_relevance": 0.89,
            "latency_p50_ms": 160.0,
            "latency_p95_ms": 290.0,
        },
    ]
    table = format_markdown_table(sample_results)
    assert "| Strategy | Rerank |" in table
    assert "`fixed`" in table
    assert "0.920" in table
