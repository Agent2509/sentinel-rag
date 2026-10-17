"""A reindex must never let a reader load a new index against old chunks.

Covers the swap/cache path that tests/test_retriever.py stubs out. Embeddings are
stubbed (no model); fixed + hierarchical chunkers are used so no embedder runs
inside a chunker.
"""
import threading

import numpy as np
import pytest

from app import config, ingest, retriever

STRATEGIES = ("fixed", "hierarchical")


@pytest.fixture
def lab(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CORPUS_DIR", tmp_path / "corpus")
    monkeypatch.setattr(config, "INDEX_DIR", tmp_path / "index")
    monkeypatch.setattr(config, "STRATEGIES", STRATEGIES)
    config.CORPUS_DIR.mkdir()
    (config.CORPUS_DIR / "a.md").write_text("alpha beta gamma delta. " * 80)
    monkeypatch.setattr(
        ingest,
        "embed_documents",
        lambda texts, show_progress=False: np.zeros((len(texts), 384), dtype="float32"),
    )
    ingest.reindex()
    retriever.reset_cache()
    yield
    retriever.reset_cache()


def test_load_matches_index_after_reindex(lab):
    for strategy in STRATEGIES:
        bundle = retriever.get_bundle(strategy)
        assert bundle.faiss_index.ntotal == len(bundle.chunks)


def test_readers_block_while_indexes_swap(lab):
    # The mismatch only appears when a load runs *during* the file swap. Hold the
    # swap open and prove a concurrent load waits, so the two files are always
    # read as a matched pair. Fails if swap_indexes stops holding the lock.
    retriever.reset_cache()
    entered, release = threading.Event(), threading.Event()

    def apply():
        entered.set()
        release.wait(5)

    swapper = threading.Thread(target=retriever.swap_indexes, args=(apply,))
    swapper.start()
    assert entered.wait(5), "swap did not start"

    got: list = []
    reader = threading.Thread(target=lambda: got.append(retriever.get_bundle("hierarchical")))
    reader.start()
    reader.join(0.3)
    blocked = reader.is_alive()  # still waiting on the lock held by the swap

    release.set()
    swapper.join(5)
    reader.join(5)

    assert blocked, "a load ran concurrently with the swap"
    assert got and got[0].faiss_index.ntotal == len(got[0].chunks)
