"""daari.http — shared outbound HTTP config for the live fetchers.

One client factory (browser UA — Groq/Remotive/myscheme all answer a default
python/urllib or bare-httpx UA with Cloudflare `error code: 1010`; 10s
timeout; follow redirects), one polite per-host rate limiter (1 req/s, an
asyncio.Lock + last-call timestamp per host), and one 15-minute TTL cache
keyed by the full request URL.

# ponytail: in-process TTL cache, move to redis if we ever run >1 worker
"""

from __future__ import annotations

import asyncio
import time
from urllib.parse import urlencode, urlparse

import httpx

# Query-param names that carry a credential. A cache key built from these
# would keep the credential alive in process memory for no benefit — the
# cache key never needs to distinguish requests only by their key value.
_SECRET_PARAM_KEYS = {"app_id", "app_key", "api_key", "x-api-key", "key"}

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
TIMEOUT_S = 10.0
POLITE_INTERVAL_S = 1.0
CACHE_TTL_S = 900.0  # 15 minutes

_host_locks: dict[str, asyncio.Lock] = {}
_host_last_call: dict[str, float] = {}
_cache: dict[str, tuple[float, object]] = {}


def new_client() -> httpx.AsyncClient:
    """The one shared client config every fetcher builds its requests on."""
    return httpx.AsyncClient(
        timeout=TIMEOUT_S,
        follow_redirects=True,
        headers={"User-Agent": BROWSER_UA},
    )


async def _polite_wait(url: str) -> None:
    host = urlparse(url).netloc
    lock = _host_locks.setdefault(host, asyncio.Lock())
    async with lock:
        last = _host_last_call.get(host, 0.0)
        remaining = POLITE_INTERVAL_S - (time.monotonic() - last)
        if remaining > 0:
            await asyncio.sleep(remaining)
        _host_last_call[host] = time.monotonic()


def _cache_key(url: str, params: dict[str, object] | None) -> str:
    if not params:
        return url
    public = {k: v for k, v in params.items() if k.lower() not in _SECRET_PARAM_KEYS}
    return f"{url}?{urlencode(sorted(public.items()))}"


async def get_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    cache_ttl_s: float = CACHE_TTL_S,
) -> object:
    """GET `url` (+ `params`), polite-limited per host and TTL-cached.

    `params` is passed through to httpx's own encoding rather than hand-built
    into the URL string — safer encoding, and it keeps a credentialed value
    (an `app_key`, an `api_key`) from ever landing in a manually-concatenated
    string that might get logged or reused as a public `source_url`. The
    cache key deliberately drops any param that looks like a credential
    (see `_SECRET_PARAM_KEYS`) so one never sits in process memory either.

    Raises `httpx.HTTPStatusError` / `httpx.RequestError` / `ValueError` on
    failure — this helper does not swallow them. Each fetcher's own
    try/except is the single place a failure becomes an empty list plus an
    error string; this stays a plain HTTP helper.
    """
    key = _cache_key(url, params)
    cached = _cache.get(key)
    if cached is not None:
        expires_at, value = cached
        if time.monotonic() < expires_at:
            return value
    await _polite_wait(url)
    resp = await client.get(url, params=params, headers=headers)
    resp.raise_for_status()
    value = resp.json()
    _cache[key] = (time.monotonic() + cache_ttl_s, value)
    return value
