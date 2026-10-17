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
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from app import config

load_dotenv()

# Every key in the environment (GROQ_API_KEY, GROQ_API_KEY_2, ...) forms a pool.
# Calls round-robin across the pool so free-tier limits from separate Groq accounts
# add up; a single-account setup just cycles its one key. The eval judge builds one
# client per key from the same pool (see eval/run_ragas.py).
_pool: list[OpenAI] = []
_rr = 0
_ready = False


def api_keys() -> list[str]:
    """All distinct Groq keys in the environment, in a stable order."""
    out: list[str] = []
    for name in sorted(os.environ):
        if name.startswith("GROQ_API_KEY"):
            val = os.environ[name]
            if val and val not in out:
                out.append(val)
    return out


def _clients() -> list[OpenAI]:
    global _pool, _ready
    if not _ready:
        keys = api_keys()
        if not keys:
            raise RuntimeError("Missing GROQ_API_KEY in environment/.env")
        _pool = [
            OpenAI(base_url=config.GROQ_BASE_URL, api_key=k, timeout=config.LLM_TIMEOUT)
            for k in keys
        ]
        _ready = True
    return _pool


def _evict(client: OpenAI) -> None:
    """Drop a key the API rejected (e.g. revoked) so it stops breaking every call."""
    global _pool
    _pool = [c for c in _pool if c is not client]


def get_client(provider: str) -> OpenAI:
    """Return the next client in the round-robin pool (provider kept for callers)."""
    global _rr
    pool = _clients()
    if not pool:
        raise RuntimeError("No usable Groq keys left")
    client = pool[_rr % len(pool)]
    _rr += 1
    return client


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
    # Try at least once per pooled key: get_client() rotates, so a 429 on one
    # account's key retries on the next account's key.
    attempts = max(retries + 1, len(_clients()))
    for attempt in range(attempts):
        client = get_client(provider)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return resp.choices[0].message.content or ""
        except AuthenticationError:
            # A revoked/invalid key must not poison the pool: drop it and use another.
            _evict(client)
            print(f"[llm] dropped a rejected key; {len(_clients())} left")
            if not _clients():
                raise
            continue
        except Exception as e:  # noqa: BLE001 - only transient errors are retried
            if attempt < attempts - 1 and _is_transient(e):
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
