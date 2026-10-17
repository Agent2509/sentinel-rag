"""Query router: classify a query as simple or complex (Groq, JSON mode)."""
from app import config, llm

_SYSTEM = (
    "You route queries for a retrieval-augmented generation system. "
    "Classify the user's query as either 'simple' or 'complex'. "
    "'simple' means a single factual lookup answerable from one short passage. "
    "'complex' means it requires comparing, multi-hop reasoning, or synthesizing "
    "multiple passages. "
    'Respond with JSON only, exactly this shape: '
    '{"type": "simple" | "complex", "reason": "<short reason>"}'
)


def route(query: str) -> dict:
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": query},
    ]
    try:
        data = llm.chat_json(
            config.GROQ_MODEL,
            messages,
            config.ROUTER_TEMP,
            config.ROUTER_MAX_TOKENS,
        )
        route_type = str(data.get("type", "")).strip().lower()
        if route_type not in ("simple", "complex"):
            raise ValueError(f"unexpected type {route_type!r}")
        return {"type": route_type, "reason": str(data.get("reason", ""))}
    except Exception as e:  # noqa: BLE001 - never fail the pipeline on routing
        return {
            "type": "complex",
            "reason": f"router failed ({type(e).__name__}); defaulting to complex",
        }
