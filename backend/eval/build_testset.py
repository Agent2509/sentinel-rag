"""Generate a reference test set from the corpus using Groq.

Each row: {doc, question, reference, reference_contexts}. The whole source doc is
used as the reference context (ground truth for context recall/precision).

    python -m eval.build_testset --limit 5
"""
import argparse
import json
from pathlib import Path

from app import config, ingest, llm

_SYSTEM = (
    "You create evaluation data from a technical passage. Write {n} question(s) "
    "that are answerable solely from the passage, each with a concise reference "
    "answer grounded in the passage. Respond with JSON only, exactly this shape: "
    '{{"items": [{{"question": "...", "answer": "..."}}]}}'
)


def parse_items(data, per_doc: int) -> list[dict]:
    """Pull clean {question, answer} pairs from a model response, defensively."""
    if not isinstance(data, dict):
        return []
    items = data.get("items")
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for item in items[:per_doc]:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        if question and answer:
            out.append({"question": question, "answer": answer})
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="0 = all docs")
    parser.add_argument("--per-doc", type=int, default=1)
    parser.add_argument("--out", default=str(Path(__file__).parent / "testset.jsonl"))
    args = parser.parse_args()

    docs = sorted(config.CORPUS_DIR.glob("*.md"))
    if args.limit:
        docs = docs[: args.limit]

    version = ingest.corpus_version()
    rows: list[dict] = []
    for path in docs:
        text = path.read_text()
        messages = [
            {"role": "system", "content": _SYSTEM.format(n=args.per_doc)},
            {"role": "user", "content": f"Passage:\n{text}"},
        ]
        try:
            data = llm.chat_json(
                "groq", config.GROQ_MODEL, messages, 0.3, 1024
            )
        except Exception as e:  # noqa: BLE001 - skip a doc rather than abort the run
            print(f"  skip {path.name}: {type(e).__name__}")
            continue
        items = parse_items(data, args.per_doc)
        if not items:
            print(f"  {path.name}: no usable items, skipped")
        for item in items:
            rows.append(
                {
                    "doc": path.name,
                    "question": item["question"],
                    "reference": item["answer"],
                    "reference_contexts": [text],
                    "corpus_version": version,
                }
            )
        print(f"  {path.name}: {len(items)} item(s)")

    if not rows:
        print("WARNING: no rows produced; check the model/keys before evaluating.")
    with open(args.out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
