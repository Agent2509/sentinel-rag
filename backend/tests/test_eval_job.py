"""Guards for the manual eval job (no subprocess, no LLM)."""
import pytest

from app import config, eval_job


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(
        eval_job,
        "_state",
        {
            "running": False,
            "stage": "idle",
            "message": None,
            "error": None,
            "corpus_version": None,
            "started_at": None,
        },
    )
    monkeypatch.setattr(config, "CORPUS_DIR", tmp_path)
    monkeypatch.setattr(config, "EVAL_MIN_DOCS", 3)
    monkeypatch.setattr(config, "EVAL_PYTHON", str(tmp_path / "missing-python"))
    return tmp_path


def seed(path, n):
    for i in range(n):
        (path / f"doc{i}.md").write_text(f"document {i}")


def test_refuses_too_few_documents(isolated):
    seed(isolated, 2)
    ok, code, message = eval_job.start()
    assert not ok and code == 400
    assert "at least 3" in message


def test_refuses_missing_eval_interpreter(isolated):
    seed(isolated, 3)
    ok, code, message = eval_job.start()
    assert not ok and code == 400
    assert "eval interpreter" in message


def test_refuses_while_running(isolated):
    seed(isolated, 3)
    eval_job._state["running"] = True
    ok, code, message = eval_job.start()
    assert not ok and code == 409
    assert "already running" in message


def test_starts_with_enough_docs_and_returns_status(isolated, monkeypatch):
    seed(isolated, 3)
    fake = isolated / "python"
    fake.write_text("")
    fake.chmod(0o755)
    monkeypatch.setattr(config, "EVAL_PYTHON", str(fake))
    started: dict = {}

    class FakeThread:
        def __init__(self, target=None, args=(), daemon=None):
            started["target"] = target
            started["args"] = args

        def start(self):
            started["called"] = True

    monkeypatch.setattr(eval_job.threading, "Thread", FakeThread)

    ok, code, message = eval_job.start()
    assert ok and code == 202 and message == "started"
    assert started["called"] is True
    status = eval_job.status()
    assert status["running"] is True
    assert status["stage"] == "starting"
    assert status["corpus_size"] == 3
    assert status["min_docs"] == 3
