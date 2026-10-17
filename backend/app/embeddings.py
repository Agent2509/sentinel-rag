"""Singleton bge-small-en-v1.5 wrapper.

BGE retrieval models expect an instruction prefix on the *query* side only;
documents are embedded raw. Vectors are L2-normalized so IndexFlatIP is
equivalent to cosine similarity.
"""
import threading

import numpy as np

from app import config

_model = None
_lock = threading.Lock()


def _load():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer

                print(
                    f"[embeddings] loading {config.EMBED_MODEL} "
                    "(first run downloads ~130MB)..."
                )
                _model = SentenceTransformer(config.EMBED_MODEL)
    return _model


def warmup() -> None:
    _load()


def is_loaded() -> bool:
    return _model is not None


def embed_documents(texts: list[str], show_progress: bool = False) -> np.ndarray:
    if not texts:
        return np.zeros((0, config.EMBED_DIM), dtype="float32")
    vectors = _load().encode(
        texts,
        batch_size=config.EMBED_BATCH,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=show_progress,
    )
    return vectors.astype("float32")


def embed_query(text: str) -> np.ndarray:
    return embed_documents([config.QUERY_PREFIX + text])[0]
