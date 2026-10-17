import sys
from pathlib import Path

# so `import app` works no matter how pytest is invoked
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
