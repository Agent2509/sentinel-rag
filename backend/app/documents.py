"""Corpus documents on disk. The directory is the source of truth (no manifest).

Uploads are normalized to `.md` and written into CORPUS_DIR; a reindex then picks
them up like any other doc. List/delete derive everything from the filesystem.
"""
import hashlib
import io
import re
import uuid
from pathlib import Path

from app import config
from app.chunkers import token_count

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")
_TEXT_SUFFIXES = {".md", ".txt"}
MAX_BYTES = 10 * 1024 * 1024


class DuplicateDocument(Exception):
    pass


def _safe_stem(name: str) -> str:
    stem = _SAFE.sub("-", Path(name).stem).strip("-")
    return (stem or "doc")[:60]


def list_documents() -> list[dict]:
    docs = []
    for path in sorted(config.CORPUS_DIR.glob("*.md")):
        docs.append(
            {
                "name": path.name,
                "tokens": token_count(path.read_text()),
                "added_at": int(path.stat().st_mtime),
            }
        )
    return docs


def extract_text(filename: str, data: bytes) -> str:
    """Normalize an uploaded file to plain text, or raise ValueError."""
    suffix = Path(filename).suffix.lower()
    if suffix in _TEXT_SUFFIXES:
        return data.decode("utf-8", errors="replace")
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"unsupported file type {suffix or '(none)'}")


def add_document(filename: str, text: str) -> str:
    # normalize newlines so CRLF uploads hash the same as their LF twin on disk
    content = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not content:
        raise ValueError("document has no extractable text")
    content += "\n"  # hash exactly what we write, so dedupe matches on disk
    digest = hashlib.sha256(content.encode()).hexdigest()
    for path in config.CORPUS_DIR.glob("*.md"):
        if hashlib.sha256(path.read_bytes()).hexdigest() == digest:
            raise DuplicateDocument(path.name)
    stored = f"{_safe_stem(filename)}-{uuid.uuid4().hex[:8]}.md"
    (config.CORPUS_DIR / stored).write_bytes(content.encode())
    return stored


def remove_document(name: str) -> None:
    path = config.CORPUS_DIR / Path(name).name  # basename only: no traversal
    if path.suffix != ".md" or not path.exists():
        raise FileNotFoundError(name)
    path.unlink()
