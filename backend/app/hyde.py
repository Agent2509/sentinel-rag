"""HyDE: generate a hypothetical document that would answer the query (Groq)."""
from app import config, llm

_SYSTEM = (
    "Write a short, factual passage of three to five sentences that would directly "
    "answer the user's question, in the style of a technical encyclopedia article. "
    "Do not restate or mention the question. Output only the passage."
)


def rewrite(query: str) -> str:
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": query},
    ]
    doc = llm.chat(
        "groq",
        config.GROQ_MODEL,
        messages,
        config.HYDE_TEMP,
        config.HYDE_MAX_TOKENS,
    )
    return doc.strip()
