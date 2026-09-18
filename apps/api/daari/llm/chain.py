"""daari.llm.chain — THE ONLY LLM ENTRY POINT (api.md).

`complete()` is the single function anything in `apps/api` may call to reach
an LLM. Provider order Gemini -> Groq -> Ollama -> cache-only. Temperature 0
everywhere: the LLM here only extracts structure or writes words, it never
decides a score (CLAUDE.md non-negotiable 3), so there is no reason for any
call in this module to be non-deterministic.

Every response is cached on disk under `settings.LLM_CACHE_DIR`, keyed by
`sha256(task + model + normalised_input)`. Each provider's cache is checked
*before* its network call, so a cache hit never touches the network — this
is what "cache-only" (the fourth link in the chain) actually is: when the
network is unplugged, every live call below fails fast and the loop falls
through provider by provider on cache hits alone.

Per-provider circuit breaker: 3 consecutive failures, or a single 429,
skips that provider for 60s. Never let one flaky provider add its own
timeout to every request behind it.

Every call logs `{task, provider, model, latency_ms, cache_hit, tool_calls}`
via structlog — never a key, never a raw prompt.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import structlog

from daari.config import settings
from daari.http import new_client
from daari.main import GEMINI_MODEL, GROQ_CHAT_MODEL, OLLAMA_MODEL

log = structlog.get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[4]
BREAKER_COOLDOWN_S = 60.0
BREAKER_FAILURE_THRESHOLD = 3


@dataclass(frozen=True)
class LLMResult:
    text: str
    provider: str
    model: str
    cache_hit: bool
    latency_ms: int


class LLMUnavailableError(RuntimeError):
    """Raised only when every provider failed or was breaker-skipped AND no
    cached response exists for any of them — i.e. there is genuinely
    nothing this function can return."""


# --- disk cache ----------------------------------------------------------


def _cache_dir() -> Path:
    path = Path(settings.LLM_CACHE_DIR)
    if not path.is_absolute():
        path = REPO_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def _normalise(prompt: str, schema: dict | None) -> str:
    body = {"prompt": prompt.strip(), "schema": schema or {}}
    return json.dumps(body, sort_keys=True, separators=(",", ":"))


def _cache_key(task: str, model: str, normalised_input: str) -> str:
    return hashlib.sha256(f"{task}:{model}:{normalised_input}".encode()).hexdigest()


def _cache_read(key: str) -> str | None:
    file = _cache_dir() / f"{key}.json"
    if not file.exists():
        return None
    try:
        return json.loads(file.read_text(encoding="utf-8"))["text"]
    except (ValueError, KeyError, OSError):
        return None


def _cache_write(key: str, text: str) -> None:
    file = _cache_dir() / f"{key}.json"
    file.write_text(json.dumps({"text": text}), encoding="utf-8")


# --- per-provider circuit breaker ----------------------------------------

_breaker: dict[str, dict[str, float]] = {}


def _breaker_tripped(provider: str) -> bool:
    state = _breaker.get(provider)
    return bool(state) and time.monotonic() < state["skip_until"]


def _breaker_record_failure(provider: str, *, is_429: bool = False) -> None:
    state = _breaker.setdefault(provider, {"fail_count": 0.0, "skip_until": 0.0})
    state["fail_count"] += 1
    if is_429 or state["fail_count"] >= BREAKER_FAILURE_THRESHOLD:
        state["skip_until"] = time.monotonic() + BREAKER_COOLDOWN_S
        state["fail_count"] = 0.0


def _breaker_record_success(provider: str) -> None:
    _breaker[provider] = {"fail_count": 0.0, "skip_until": 0.0}


# --- provider calls (temperature 0 everywhere) ----------------------------


async def _call_gemini(prompt: str, schema: dict | None) -> str:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("no_api_key")
    body: dict = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0},
    }
    if schema:
        body["generationConfig"]["response_mime_type"] = "application/json"
        body["generationConfig"]["response_schema"] = schema
    async with new_client() as client:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
            params={"key": settings.GEMINI_API_KEY},
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


async def _call_groq(prompt: str, schema: dict | None) -> str:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("no_api_key")
    body: dict = {
        "model": GROQ_CHAT_MODEL,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    if schema:
        body["response_format"] = {"type": "json_object"}
    async with new_client() as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"]


async def _call_ollama(prompt: str, schema: dict | None) -> str:
    body: dict = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0},
    }
    if schema:
        body["format"] = "json"
    async with new_client() as client:
        resp = await client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=body)
        resp.raise_for_status()
        data = resp.json()
    return data["response"]


_PROVIDERS = (
    ("gemini", GEMINI_MODEL, _call_gemini),
    ("groq", GROQ_CHAT_MODEL, _call_groq),
    ("ollama", OLLAMA_MODEL, _call_ollama),
)


async def complete(task: str, prompt: str, *, schema: dict | None = None) -> LLMResult:
    """The only LLM entry point. Tries Gemini, Groq, Ollama in order; each
    provider's disk cache is checked before its network call, so a cached
    task works with the network unplugged (CLAUDE.md non-negotiable 7).

    Raises `LLMUnavailableError` only when every provider is breaker-skipped
    or failed AND none of the three has a cached response for this input.
    """
    normalised = _normalise(prompt, schema)

    for provider, model, call_fn in _PROVIDERS:
        key = _cache_key(task, model, normalised)
        cached = _cache_read(key)
        if cached is not None:
            log.info(
                "llm_call",
                task=task,
                provider=provider,
                model=model,
                latency_ms=0,
                cache_hit=True,
                tool_calls=0,
            )
            return LLMResult(text=cached, provider=provider, model=model, cache_hit=True, latency_ms=0)

        if _breaker_tripped(provider):
            continue

        t0 = time.monotonic()
        try:
            text = await call_fn(prompt, schema)
        except httpx.HTTPStatusError as exc:
            _breaker_record_failure(provider, is_429=exc.response.status_code == 429)
            continue
        except (httpx.RequestError, RuntimeError, KeyError, ValueError):
            _breaker_record_failure(provider)
            continue

        latency_ms = round((time.monotonic() - t0) * 1000)
        _breaker_record_success(provider)
        _cache_write(key, text)
        log.info(
            "llm_call",
            task=task,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            cache_hit=False,
            tool_calls=0,
        )
        return LLMResult(text=text, provider=provider, model=model, cache_hit=False, latency_ms=latency_ms)

    log.info("llm_call", task=task, provider="none", model="none", latency_ms=0, cache_hit=False, tool_calls=0)
    raise LLMUnavailableError(f"no provider available and no cache hit for task={task!r}")
