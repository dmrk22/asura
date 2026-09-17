# api.md — apps/api

- Python 3.12 via `uv`. FastAPI + Pydantic v2 + SQLAlchemy 2 async + Alembic + structlog. Run everything through `uv run`.
- Schema changes are Alembic autogenerate, never hand-edited SQL: `uv run alembic revision --autogenerate -m "<msg>" && uv run alembic upgrade head`.
- `llm.complete()` / `llm.vision()` are the only LLM entry points. Provider order Gemini → Groq → Ollama → cache, per-provider circuit breaker (3 failures or one 429 → skip 60 s), token bucket from the free-tier RPM in `config.py`, every response cached by `sha256(task + model + normalised input)`.
- Determinism: temperature 0 everywhere; router seed from `ROUTER_SEED`; embeddings frozen (`BAAI/bge-small-en-v1.5`); log `{task, provider, model, latency_ms, cache_hit, tier}` on every call.
- `enforce(profile, plan) -> (plan', Trace[])` is **pure**: no I/O, no clock, no randomness. Hypothesis tests assert idempotence and that banned items never survive.
- One clock per measurement. Stamp `t_emit` in the simulator and carry it; never re-read the clock and call it the same instant.
- `worker.py` handles SIGINT and SIGTERM: drain the consumer group, ack in flight, exit 0.
- Structured logs only. Never log a key, a token, or a connection string.
