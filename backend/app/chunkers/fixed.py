"""Fixed-size chunker: 512 tokens with 50-token overlap."""
from app import config
from app.chunkers import Chunk, get_encoder


def chunk(text: str, doc_title: str) -> list[Chunk]:
    enc = get_encoder()
    ids = enc.encode(text)
    size = config.FIXED_CHUNK_TOKENS
    step = size - config.FIXED_OVERLAP_TOKENS
    chunks: list[Chunk] = []
    i = 0
    while i < len(ids):
        window = ids[i : i + size]
        chunks.append(
            Chunk(doc_title=doc_title, text=enc.decode(window), strategy="fixed")
        )
        if i + size >= len(ids):
            break
        i += step
    return chunks
