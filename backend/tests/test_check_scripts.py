"""Run the deterministic self-check scripts; a nonzero exit fails the suite."""
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = ["check_pipeline", "check_api", "check_documents", "check_eval"]


@pytest.mark.parametrize("script", SCRIPTS)
def test_check_script(script):
    proc = subprocess.run(
        [sys.executable, f"scripts/{script}.py"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"{script} failed:\n{proc.stdout}\n{proc.stderr}"
