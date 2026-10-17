"""Milestone 1 gate: query every FAISS + BM25 index, print top hits.

    python -m app.verify
"""
from app import config
from app.retriever import bm25_search, get_bundle, vector_search

QUERIES = [
    "how does the attention mechanism work in transformers",
    "what is the difference between LSTM and RNN",
    "how does HyDE improve retrieval",
    "explain reciprocal rank fusion for hybrid search",
    "what is LoRA parameter efficient fine tuning",
]


def show(title: str, chunks: list, ids: list[int], k: int = 3) -> None:
    print(f"    {title}:")
    for idx in ids[:k]:
        c = chunks[idx]
        snippet = " ".join(c.text.split())[:90]
        print(f"      [{idx:3d}] {c.chunk_id} ({c.doc_title}) :: {snippet}")


def main() -> None:
    for strategy in config.STRATEGIES:
        print(f"\n=== {strategy} ===")
        bundle = get_bundle(strategy)
        print(f"  {len(bundle.chunks)} chunks indexed")
        for query in QUERIES:
            print(f"  Q: {query}")
            show("BM25", bundle.chunks, bm25_search(bundle, query, 20))
            show("FAISS", bundle.chunks, vector_search(bundle, query, 20))


if __name__ == "__main__":
    main()
