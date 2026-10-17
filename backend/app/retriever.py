"""Hybrid retrieval: BM25 + FAISS, fused with Reciprocal Rank Fusion."""
import threading
from collections.abc import Callable

import numpy as np

from app import config
from app.embeddings import embed_documents, embed_query
from app.store import IndexBundle, load_strategy, tokenize

_bundles: dict[str, IndexBundle] = {}
_lock = threading.Lock()


def get_bundle(strategy: str) -> IndexBundle:
    with _lock:
        if strategy not in _bundles:
            _bundles[strategy] = load_strategy(strategy)
        return _bundles[strategy]


def reset_cache() -> None:
    """Drop cached indexes so the next query reloads them (after a reindex)."""
    with _lock:
        _bundles.clear()


def swap_indexes(apply: "Callable[[], None]") -> None:
    """Swap the live index files and drop the cache as one critical section.

    `apply` does the file renames. Holding `_lock` here means a concurrent
    get_bundle() cannot load a new .faiss against an old chunks.json. Clearing
    the cache inline (not via reset_cache) avoids re-acquiring a non-reentrant
    Lock on the same thread.
    """
    with _lock:
        apply()
        _bundles.clear()


def bm25_search(bundle: IndexBundle, query: str, k: int) -> list[int]:
    scores = np.asarray(bundle.bm25.get_scores(tokenize(query)))
    order = np.argsort(scores)[::-1][: min(k, len(scores))]
    # zero score = no lexical match; those hits would only pollute RRF fusion
    return [int(i) for i in order if scores[i] > 0]


def vector_search(
    bundle: IndexBundle, query: str, k: int, as_query: bool = True
) -> list[int]:
    # as_query=True -> bge query instruction prefix; False -> embed raw (HyDE doc).
    vec = embed_query(query) if as_query else embed_documents([query])[0]
    q = vec.reshape(1, -1).astype("float32")
    k = min(k, len(bundle.chunks))
    _, idx = bundle.faiss_index.search(q, k)
    return [int(i) for i in idx[0] if i >= 0]


def hybrid_search(
    strategy: str,
    query: str,
    k_final: int = config.FINAL_TOP_K,
    as_query: bool = True,
) -> list[dict]:
    bundle = get_bundle(strategy)
    bm25_ids = bm25_search(bundle, query, config.BM25_TOP_K)
    vector_ids = vector_search(bundle, query, config.VECTOR_TOP_K, as_query=as_query)

    bm25_rank = {idx: r for r, idx in enumerate(bm25_ids)}
    vector_rank = {idx: r for r, idx in enumerate(vector_ids)}

    rrf: dict[int, float] = {}
    for idx, r in bm25_rank.items():
        rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (config.RRF_K + r + 1)
    for idx, r in vector_rank.items():
        rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (config.RRF_K + r + 1)

    top = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:k_final]
    results = []
    for idx, score in top:
        c = bundle.chunks[idx]
        results.append(
            {
                "chunk_id": c.chunk_id,
                "doc_title": c.doc_title,
                "text": c.text,
                "parent_id": c.parent_id,
                "parent_text": c.parent_text,
                "bm25_rank": bm25_rank.get(idx),
                "vector_rank": vector_rank.get(idx),
                "rrf_score": score,
            }
        )
    return results
