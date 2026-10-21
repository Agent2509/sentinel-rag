"""Singleton cross-encoder reranker.

Reranks candidate chunks retrieved via hybrid search (BM25 + FAISS / RRF)
by computing a deep joint attention score between the query and each chunk.
"""
from __future__ import annotations

import threading
from typing import Any

from app import config

_model: Any = None
_lock = threading.Lock()


def _load() -> Any:
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import CrossEncoder

                print(
                    f"[reranker] loading {config.RERANKER_MODEL} "
                    "(first run downloads model weights)..."
                )
                _model = CrossEncoder(config.RERANKER_MODEL)
    return _model


def warmup() -> None:
    """Preload model weights into memory."""
    _load()


def is_loaded() -> bool:
    return _model is not None


def rerank(
    query: str,
    chunks: list[dict[str, Any]],
    top_n: int = config.FINAL_TOP_K,
) -> list[dict[str, Any]]:
    """Score and sort chunks using the cross-encoder model.

    Takes the top-K candidate chunks (e.g. 15 from RRF) and scores them
    jointly with the query, returning the top-N highest scoring chunks.
    Falls back safely to the original chunk ranking if scoring fails.
    """
    if not chunks or top_n <= 0:
        return []

    try:
        model = _load()
        # Pair query with each chunk's text (or context if present)
        pairs = [(query, c.get("text", "")) for c in chunks]
        scores = model.predict(pairs)

        # Attach rerank_score to shallow copy of each chunk
        scored_chunks = []
        for c, score in zip(chunks, scores):
            item = dict(c)
            item["rerank_score"] = float(score)
            scored_chunks.append(item)

        scored_chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_chunks[:top_n]
    except Exception as e:
        print(f"[reranker] Warning: reranking failed ({type(e).__name__}: {e}), using original order")
        return [dict(c) for c in chunks[:top_n]]
