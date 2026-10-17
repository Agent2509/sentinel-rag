"""Shared chunk type + tokenizer. Chunkers are duck-typed functions:

    chunk(text: str, doc_title: str) -> list[Chunk]
"""
from dataclasses import dataclass, asdict
from functools import lru_cache

from app import config


@dataclass
class Chunk:
    chunk_id: str = ""
    doc_title: str = ""
    text: str = ""
    parent_id: str | None = None
    parent_text: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Chunk":
        return cls(
            chunk_id=d.get("chunk_id", ""),
            doc_title=d.get("doc_title", ""),
            text=d.get("text", ""),
            parent_id=d.get("parent_id"),
            parent_text=d.get("parent_text"),
        )


@lru_cache(maxsize=1)
def get_encoder():
    import tiktoken

    return tiktoken.get_encoding(config.TOKENIZER_ENCODING)


def token_count(text: str) -> int:
    return len(get_encoder().encode(text))
