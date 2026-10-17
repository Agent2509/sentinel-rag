"""Load/save per-strategy FAISS + BM25 indexes and chunk metadata."""
import json
import pickle
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
    from rank_bm25 import BM25Okapi

    out = out_dir or config.INDEX_DIR
    out.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(out / f"{name}.faiss"))

    corpus_tokens = [tokenize(c.text) for c in chunks]
    bm25 = BM25Okapi(corpus_tokens)
    with open(out / f"{name}.bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)

    with open(out / f"{name}.chunks.json", "w") as f:
        json.dump([c.to_dict() for c in chunks], f)


def load_strategy(name: str) -> IndexBundle:
    index = faiss.read_index(str(config.INDEX_DIR / f"{name}.faiss"))
    with open(config.INDEX_DIR / f"{name}.bm25.pkl", "rb") as f:
        bm25 = pickle.load(f)
    with open(config.INDEX_DIR / f"{name}.chunks.json") as f:
        chunks = [Chunk.from_dict(d) for d in json.load(f)]
    return IndexBundle(chunks=chunks, faiss_index=index, bm25=bm25)


def indexes_exist() -> bool:
    return all(
        (config.INDEX_DIR / f"{s}.{ext}").exists()
        for s in config.STRATEGIES
        for ext in ("faiss", "bm25.pkl", "chunks.json")
    )
