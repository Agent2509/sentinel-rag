"""RRF fusion and zero-score BM25 filtering (no model, no network)."""
from app import retriever
from app.chunkers import Chunk
from app.store import IndexBundle


class FakeBM25:
    def __init__(self, scores):
        self.scores = scores

    def get_scores(self, tokens):
        return self.scores


def make_bundle(scores):
    chunks = [
        Chunk(
            text=f"t{i}",
            doc_title=f"d{i}",
            chunk_id=f"c{i}",
            parent_id=None,
        )
        for i in range(len(scores))
    ]
    return IndexBundle(chunks=chunks, faiss_index=None, bm25=FakeBM25(scores))


def test_zero_score_bm25_hits_are_dropped():
    bundle = make_bundle([0.0, 5.0, 0.0, 3.0])
    assert retriever.bm25_search(bundle, "query", 4) == [1, 3]


def test_bm25_respects_k():
    bundle = make_bundle([1.0, 5.0, 3.0])
    assert retriever.bm25_search(bundle, "query", 2) == [1, 2]


def test_rrf_fusion_prefers_shared_ranks(monkeypatch):
    bundle = make_bundle([5.0, 4.0, 0.0, 3.0])
    monkeypatch.setattr(retriever, "get_bundle", lambda s: bundle)
    monkeypatch.setattr(
        retriever, "vector_search", lambda b, q, k, as_query=True: [2, 0]
    )
    results = retriever.hybrid_search("fixed", "query", k_final=3)
    ids = [r["chunk_id"] for r in results]
    # bm25 hits [0, 1, 3] (zero score on c2 dropped), vector hits [2, 0]
    # c0 appears in both lists -> largest rrf score -> first despite being the
    # vector runner-up; c2 (vector rank 0) beats c1 (bm25 rank 1)
    assert ids == ["c0", "c2", "c1"]
    by_id = {r["chunk_id"]: r for r in results}
    assert by_id["c0"]["bm25_rank"] == 0 and by_id["c0"]["vector_rank"] == 1
    assert by_id["c2"]["vector_rank"] == 0 and by_id["c2"]["bm25_rank"] is None
