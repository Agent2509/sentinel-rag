"""Manual RAGAS evaluation job.

RAGAS conflicts with the runtime pins (see requirements-eval.txt), so this job
shells out to the isolated eval interpreter instead of importing it here.
One job at a time; progress is polled through /api/eval/status.
"""
import subprocess
import threading
import time
from pathlib import Path

from app import config, ingest

LOG_PATH = config.INDEX_DIR / "eval_job.log"
TESTSET_PATH = config.INDEX_DIR / "testset.jsonl"
RESULTS_PATH = config.INDEX_DIR / "results.json"

_lock = threading.Lock()
_proc: subprocess.Popen | None = None
_state: dict = {
    "running": False,
    "stage": "idle",
    "message": None,
    "error": None,
    "corpus_version": None,
    "started_at": None,
}


def corpus_size() -> int:
    return len(list(config.CORPUS_DIR.glob("*.md")))


def eval_python() -> Path:
    return Path(config.EVAL_PYTHON)


def status() -> dict:
    with _lock:
        snapshot = dict(_state)
    return {
        **snapshot,
        "corpus_size": corpus_size(),
        "min_docs": config.EVAL_MIN_DOCS,
    }


def _set(**values) -> None:
    with _lock:
        _state.update(values)


def _log(text: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(text + "\n")


def _stream(cmd: list[str]) -> bool:
    global _proc
    _log(f"\n$ {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        cwd=config.BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    with _lock:
        _proc = proc
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip()
            if not line:
                continue
            _log(line)
            _set(message=line[:200])
        return proc.wait() == 0
    finally:
        with _lock:
            _proc = None


def _run(version: str) -> None:
    try:
        _set(stage="testset", message="generating a test set from the corpus")
        if not _stream(
            [
                str(eval_python()),
                "-u",
                "-m",
                "eval.build_testset",
                "--per-doc",
                "1",
                "--out",
                str(TESTSET_PATH),
            ]
        ):
            raise RuntimeError("test-set generation failed (see eval_job.log)")

        if ingest.corpus_version() != version:
            raise RuntimeError("corpus changed during test-set generation; re-run")

        _set(stage="evaluating", message="running the RAGAS matrix")
        if not _stream(
            [
                str(eval_python()),
                "-u",
                "-m",
                "eval.run_ragas",
                "--testset",
                str(TESTSET_PATH),
                "--out",
                str(RESULTS_PATH),
                "--limit",
                str(config.EVAL_ROWS),
                "--concurrency",
                "2",
                "--pace",
                "1",
                "--correction",
                "both",
            ]
        ):
            raise RuntimeError("evaluation failed (see eval_job.log)")

        if ingest.corpus_version() != version:
            _set(
                stage="done",
                message="finished, but the corpus changed mid-run — results carry the old version",
            )
        else:
            _set(stage="done", message="finished")
    except Exception as e:  # noqa: BLE001 - surfaced through status()
        _set(stage="error", message="failed", error=f"{type(e).__name__}: {e}")
    finally:
        _set(running=False)


def start() -> tuple[bool, int, str]:
    """Returns (ok, http_status, message)."""
    if ingest.is_running():
        return False, 409, "a reindex is running; wait for it to finish"
    with _lock:
        if _state["running"]:
            return False, 409, "an evaluation is already running"
    if corpus_size() < config.EVAL_MIN_DOCS:
        return False, 400, (
            f"need at least {config.EVAL_MIN_DOCS} documents; you have {corpus_size()}"
        )
    if not eval_python().exists():
        return False, 400, (
            f"eval interpreter not found at {eval_python()} — create .venv-eval "
            "(see requirements-eval.txt)"
        )

    version = ingest.corpus_version()
    with _lock:
        if _state["running"]:
            return False, 409, "an evaluation is already running"
        _state.update(
            running=True,
            stage="starting",
            message="starting",
            error=None,
            corpus_version=version,
            started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
    threading.Thread(target=_run, args=(version,), daemon=True).start()
    return True, 202, "started"
