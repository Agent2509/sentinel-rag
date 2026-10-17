"""Semantic chunker: split where consecutive-sentence similarity dips below the
25th percentile of all consecutive similarities. Groups are then capped at
SEMANTIC_MAX_CHUNK_TOKENS so no chunk exceeds the embedding model's limit.
"""
import re

import numpy as np

from app import config
from app.chunkers import Chunk, get_encoder

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in _SENTENCE_RE.split(text.strip())]
    return [p for p in parts if p]


def _cap_tokens(sentences: list[str], max_tokens: int) -> list[str]:
    enc = get_encoder()
    # Hard-split any single sentence that alone exceeds the cap, so no chunk ever
    # exceeds the embedding model's limit.
    # ponytail: splits mid-sentence at a token boundary. Fine because an oversize
    # chunk would be silently truncated by the embedder anyway; make it
    # sentence-aware only if mid-sentence cuts visibly hurt retrieval.
    pieces: list[str] = []
    for sent in sentences:
        ids = enc.encode(sent)
        if len(ids) <= max_tokens:
            pieces.append(sent)
        else:
            for i in range(0, len(ids), max_tokens):
                pieces.append(enc.decode(ids[i : i + max_tokens]))

    groups: list[str] = []
    current: list[str] = []
    current_len = 0
    for piece in pieces:
        n = len(enc.encode(piece))
        if current and current_len + n > max_tokens:
            groups.append(" ".join(current))
            current, current_len = [], 0
        current.append(piece)
        current_len += n
    if current:
        groups.append(" ".join(current))
    return groups


def chunk(text: str, doc_title: str) -> list[Chunk]:
    text = text.strip()
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return [Chunk(doc_title=doc_title, text=text)]

    from app.embeddings import embed_documents

    vectors = embed_documents(sentences)
    sims = np.sum(vectors[:-1] * vectors[1:], axis=1)
    threshold = float(np.percentile(sims, config.SEMANTIC_BREAKPOINT_PERCENTILE))

    groups: list[list[str]] = [[sentences[0]]]
    for i, sim in enumerate(sims):
        if sim < threshold:
            groups.append([])
        groups[-1].append(sentences[i + 1])

    group_texts: list[str] = []
    for group in groups:
        group_texts.extend(_cap_tokens(group, config.SEMANTIC_MAX_CHUNK_TOKENS))

    return [
        Chunk(doc_title=doc_title, text=g) for g in group_texts if g
    ]
