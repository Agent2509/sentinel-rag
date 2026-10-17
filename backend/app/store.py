"""Load/save per-strategy FAISS + BM25 indexes and chunk metadata.

BM25 is rebuilt from chunks.json at load time rather than serialized: it is
cheap to recompute and avoids pickling executable objects.
"""
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app import config
from app.chunkers import Chunk

_WORD_RE = re.compile(r"[^a-z0-9\s]")


@dataclass
class IndexBundle:
    chunks: list[Chunk]
    faiss_index: "faiss.Index"
    bm25: Any


def tokenize(text: str) -> list[str]:
    return _WORD_RE.sub(" ", text.lower()).split()


def save_strategy(
    name: str, chunks: list[Chunk], vectors: np.ndarray, out_dir: "Path | None" = None
) -> None:
    out = out_dir or config.INDEX_DIR
    out.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(out / f"{name}.faiss"))

    with open(out / f"{name}.chunks.json", "w") as f:
        json.dump([c.to_dict() for c in chunks], f)


def load_strategy(name: str) -> IndexBundle:
    from rank_bm25 import BM25Okapi

    index = faiss.read_index(str(config.INDEX_DIR / f"{name}.faiss"))
    with open(config.INDEX_DIR / f"{name}.chunks.json") as f:
        chunks = [Chunk.from_dict(d) for d in json.load(f)]
    bm25 = BM25Okapi([tokenize(c.text) for c in chunks])
    if index.ntotal != len(chunks):
        # tripwire: a mismatched pair means a half-completed swap. Fail loudly
        # rather than returning the wrong chunk for an in-range id.
        raise RuntimeError(
            f"{name}: index has {index.ntotal} vectors but {len(chunks)} chunks"
        )
    return IndexBundle(chunks=chunks, faiss_index=index, bm25=bm25)


def indexes_exist() -> bool:
    return all(
        (config.INDEX_DIR / f"{s}.{ext}").exists()
        for s in config.STRATEGIES
        for ext in ("faiss", "chunks.json")
    )
