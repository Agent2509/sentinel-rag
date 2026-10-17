"""Hierarchical chunker: parent 1024 tokens, child 256 tokens.

Child text is what gets embedded/retrieved; the parent text is stashed on each
child (parent_text) so generation can expand to the wider context.

ponytail: parent_text is duplicated per child instead of a side table. Fine for
a ~40-doc corpus; switch to a parent_id -> text map if the corpus grows.
"""
from app import config
from app.chunkers import Chunk, get_encoder


def chunk(text: str, doc_title: str) -> list[Chunk]:
    enc = get_encoder()
    ids = enc.encode(text)
    psize = config.HIER_PARENT_TOKENS
    csize = config.HIER_CHILD_TOKENS

    chunks: list[Chunk] = []
    pi = 0
    i = 0
    while i < len(ids):
        parent_ids = ids[i : i + psize]
        parent_text = enc.decode(parent_ids)
        parent_id = f"{doc_title}#p{pi:04d}"
        j = 0
        while j < len(parent_ids):
            child_ids = parent_ids[j : j + csize]
            chunks.append(
                Chunk(
                    doc_title=doc_title,
                    text=enc.decode(child_ids),
                    strategy="hierarchical",
                    parent_id=parent_id,
                    parent_text=parent_text,
                )
            )
            if j + csize >= len(parent_ids):
                break
            j += csize
        pi += 1
        if i + psize >= len(ids):
            break
        i += psize
    return chunks
