"""Generate the synthetic corpus: 50 markdown docs across the AI/ML spectrum.

Content lives in corpus_part1..5.py, each ~10 docs of roughly 600-700 tokens so
every chunking strategy (fixed 512, hierarchical 256/1024, semantic) actually
splits documents.

    python scripts/gen_corpus.py
"""
from pathlib import Path

import corpus_extras_a
import corpus_extras_b
import corpus_part1
import corpus_part2
import corpus_part3
import corpus_part4
import corpus_part5

CORPUS_DIR = Path(__file__).resolve().parents[1] / "data" / "corpus"

DOCS: dict[str, str] = {}
for part in (corpus_part1, corpus_part2, corpus_part3, corpus_part4, corpus_part5):
    DOCS.update(part.DOCS)

EXTRAS: dict[str, str] = {**corpus_extras_a.EXTRA, **corpus_extras_b.EXTRA}
for name, extra in EXTRAS.items():
    DOCS[name] = DOCS[name].rstrip() + "\n" + extra.strip() + "\n"


def main() -> None:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in DOCS.items():
        (CORPUS_DIR / name).write_text(content.strip() + "\n")
    print(f"Wrote {len(DOCS)} docs to {CORPUS_DIR}")


if __name__ == "__main__":
    main()
