"""Thin helper over the OpenAI SDK. Groq is OpenAI-compatible, so one client
factory + one chat call covers the provider. No wrapper class.
"""
import json
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from app import config

load_dotenv()

# One client per provider. Router/grader/HyDE and generation use separate Groq keys
# so generation (the big token consumer) doesn't starve the decision calls.
# The eval judge picks its own key directly (see eval/run_ragas.py), not this client.
_PROVIDERS = {
    "groq": (config.GROQ_BASE_URL, ("GROQ_API_KEY",)),
    "groq_gen": (config.GROQ_BASE_URL, ("GROQ_API_KEY_2", "GROQ_API_KEY")),
}
_clients: dict[str, OpenAI] = {}


def get_client(provider: str) -> OpenAI:
    if provider not in _clients:
        base_url, env_keys = _PROVIDERS[provider]
        key = next((os.getenv(k) for k in env_keys if os.getenv(k)), None)
        if not key:
            raise RuntimeError(f"Missing {env_keys[0]} in environment/.env")
        _clients[provider] = OpenAI(
            base_url=base_url, api_key=key, timeout=config.LLM_TIMEOUT
        )
    return _clients[provider]


def _is_transient(e: Exception) -> bool:
    """Only retry errors that a retry could actually fix."""
    if isinstance(e, (APITimeoutError, APIConnectionError, RateLimitError)):
        return True
    if isinstance(e, APIStatusError):
        return e.status_code >= 500 or e.status_code == 429
    return False


def _ensure_json_hint(messages: list[Any]) -> list[Any]:
    if any("json" in str(m.get("content", "")).lower() for m in messages):
        return messages
    return [
        *messages,
        {"role": "system", "content": "Respond with a single valid JSON object."},
    ]


def chat(
    provider: str,
    model: str,
    messages: list[Any],
    temperature: float,
    max_tokens: int,
    json_mode: bool = False,
    retries: int = config.LLM_MAX_RETRIES,
) -> str:
    if json_mode:
        messages = _ensure_json_hint(messages)
        kwargs: dict[str, Any] = {"response_format": {"type": "json_object"}}
    else:
        kwargs = {}
    for attempt in range(retries + 1):
        try:
            resp = get_client(provider).chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:  # noqa: BLE001 - only transient errors are retried
            if attempt < retries and _is_transient(e):
                time.sleep(config.LLM_RETRY_BACKOFF * (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def chat_json(
    provider: str,
    model: str,
    messages: list[Any],
    temperature: float,
    max_tokens: int,
    retries: int = config.LLM_MAX_RETRIES,
) -> dict:
    """Chat in JSON mode and return the parsed object (fences tolerated).

    Retries the whole call+parse on a malformed-JSON response, since reasoning
    models occasionally emit invalid JSON even in json_object mode.
    """
    for attempt in range(retries + 1):
        try:
            raw = chat(
                provider,
                model,
                messages,
                temperature,
                max_tokens,
                json_mode=True,
                retries=0,
            )
            return extract_json(raw)
        except Exception as e:  # noqa: BLE001
            retryable = _is_transient(e) or isinstance(e, json.JSONDecodeError)
            if attempt < retries and retryable:
                time.sleep(config.LLM_RETRY_BACKOFF * (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> dict:
    """Parse JSON, tolerating ```json fences and leading chatter."""
    match = _FENCE_RE.search(text)
    if match:
        text = match.group(1)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
        raise
