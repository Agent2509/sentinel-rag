"""Upload dedupe must survive newline-style differences (CRLF vs LF)."""
import pytest

from app import config, documents


@pytest.fixture(autouse=True)
def tmp_corpus(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CORPUS_DIR", tmp_path / "corpus")
    config.CORPUS_DIR.mkdir()
    yield config.CORPUS_DIR


def test_crlf_upload_dedupes_against_lf(tmp_corpus):
    documents.add_document("a.md", "hello\nworld")
    with pytest.raises(documents.DuplicateDocument):
        documents.add_document("b.md", "hello\r\nworld\r\n")


def test_same_content_without_trailing_newline_duplicates(tmp_corpus):
    documents.add_document("a.md", "hello world\n")
    with pytest.raises(documents.DuplicateDocument):
        documents.add_document("b.md", "hello world")


def test_different_content_stored_with_safe_name(tmp_corpus):
    stored = documents.add_document("my notes!.md", "different text")
    assert stored.endswith(".md") and " " not in stored
    assert (tmp_corpus / stored).read_bytes() == b"different text\n"
