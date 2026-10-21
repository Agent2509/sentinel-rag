"""Unit tests for the Cross-Encoder reranker module."""
from unittest.mock import MagicMock
import pytest

from app import config, reranker, retriever
from app.chunkers import Chunk
from app.store import IndexBundle


def test_rerank_empty_or_zero():
    assert reranker.rerank("query", []) == []
    assert reranker.rerank("query", [{"text": "hello"}], top_n=0) == []


def test_rerank_scores_and_sorts(monkeypatch):
    mock_model = MagicMock()
    # Return higher score for c2 than c1
    mock_model.predict.return_value = [0.12, 0.88]
    monkeypatch.setattr(reranker, "_load", lambda: mock_model)

    chunks = [
        {"chunk_id": "c1", "text": "passage 1", "rrf_score": 0.05},
        {"chunk_id": "c2", "text": "passage 2", "rrf_score": 0.02},
    ]

    reranked = reranker.rerank("target query", chunks, top_n=2)

    assert len(reranked) == 2
    # c2 had higher score (0.88 vs 0.12), so it must be first
    assert reranked[0]["chunk_id"] == "c2"
    assert reranked[0]["rerank_score"] == pytest.approx(0.88)
    assert reranked[1]["chunk_id"] == "c1"
    assert reranked[1]["rerank_score"] == pytest.approx(0.12)


def test_rerank_fallback_on_exception(monkeypatch):
    mock_model = MagicMock()
    mock_model.predict.side_effect = RuntimeError("GPU out of memory or model error")
    monkeypatch.setattr(reranker, "_load", lambda: mock_model)

    chunks = [
        {"chunk_id": "c1", "text": "passage 1"},
        {"chunk_id": "c2", "text": "passage 2"},
    ]

    # Must not raise; must return original order
    fallback_res = reranker.rerank("query", chunks, top_n=1)
    assert len(fallback_res) == 1
    assert fallback_res[0]["chunk_id"] == "c1"


def test_hybrid_search_calls_reranker(monkeypatch):
    chunks = [
        Chunk(text=f"text {i}", doc_title=f"doc {i}", chunk_id=f"c{i}", parent_id=None)
        for i in range(10)
    ]
    bundle = IndexBundle(chunks=chunks, faiss_index=None, bm25=MagicMock())
    bundle.bm25.get_scores.return_value = [float(i) for i in range(10)]

    monkeypatch.setattr(retriever, "get_bundle", lambda s: bundle)
    monkeypatch.setattr(
        retriever, "vector_search", lambda b, q, k, as_query=True: list(range(10))
    )

    rerank_called = []

    def mock_rerank(query, candidates, top_n):
        rerank_called.append((query, len(candidates), top_n))
        # reverse candidate order to verify it took effect
        return list(reversed(candidates))[:top_n]

    monkeypatch.setattr(reranker, "rerank", mock_rerank)

    res = retriever.hybrid_search("fixed", "attention query", k_final=3, rerank=True)
    assert len(rerank_called) == 1
    q, cand_len, top_n = rerank_called[0]
    assert q == "attention query"
    assert top_n == 3
    assert len(res) == 3
