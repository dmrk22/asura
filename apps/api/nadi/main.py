"""NADI API. /health is the setup exit criterion: it reports what is actually live."""
import subprocess

import redis.asyncio as aioredis
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from nadi.config import settings

app = FastAPI(title="NADI", version="0.1.0")


def _sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


async def _db_ok() -> str:
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return "ok"
    except Exception as exc:
        return f"down: {type(exc).__name__}"


async def _redis_ok() -> str:
    try:
        client = aioredis.from_url(settings.redis_url)
        await client.ping()
        await client.aclose()
        return "ok"
    except Exception as exc:
        return f"down: {type(exc).__name__}"


def _llm_providers() -> list[str]:
    """Which providers are configured. Presence of a key, not a live call — /health stays fast."""
    live = []
    if settings.gemini_api_key:
        live.append("gemini")
    if settings.groq_api_key:
        live.append("groq")
    live.append("cache")
    return live


@app.get("/health")
async def health() -> dict:
    return {
        "sha": _sha(),
        "db": await _db_ok(),
        "redis": await _redis_ok(),
        "llm": _llm_providers(),
    }
