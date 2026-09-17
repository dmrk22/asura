# api.md — apps/api (`daari`)

- Python 3.12 via `uv`. FastAPI + Pydantic v2 + SQLAlchemy 2 async + Alembic + structlog + httpx + arq. Run everything through `uv run`.
- Schema changes are Alembic autogenerate, never hand-edited SQL: `uv run alembic revision --autogenerate -m "<msg>" && uv run alembic upgrade head`.
- **`llm/chain.py` is the only LLM entry point.** Provider order Gemini → Groq → Ollama → cache. Per-provider circuit breaker (3 failures or one 429 → skip 60 s). Every response cached by `sha256(task + model + normalised input)`. Temperature 0 everywhere. Log `{task, provider, model, latency_ms, cache_hit, tool_calls}` on every call.
- `llm/tools.py` normalises tool schemas across providers and emulates tool calls via JSON mode when a provider lacks them. Adding a provider means adding a normaliser, not a branch at the call site.
- **The agent decides nothing.** `agent/loop.py` runs ≤ 6 tool calls; every call is appended to the trace with `{tool, args, ms, provider}`. A test compares every number in the final reply against the trace — a number that never appeared in a tool result is a failure.
- **Leads carry provenance.** Every `Lead` and scheme has `source`, `source_url` and `fetched_at`. A repo-scan test forbids lead literals outside `tests/fixtures/` and `mocks/`. Polite scraping: 1 req/s, 15-minute cache. SerpAPI is budgeted (≤ 30 calls at rehearsal); the remaining budget is reported by `/health`.
- **Eligibility is deterministic.** `extract_rules.py` uses the LLM at temperature 0 to produce a predicate AST with a justifying snippet per predicate; `daari_core.eligibility.evaluate()` decides. `Unknown` renders as "we need one thing", never as "qualifies".
- **Interview feedback passes `interview/guard.py`.** Every item needs a verbatim quote that is a real substring of the transcript. Violation → one rewrite at temperature 0 quoting the violation → still violating → the metrics-only template. There is no third path and no bypass flag.
- Voice: five stamps (`t_release`, `t_asr_final`, `t_llm_first_token`, `t_engine_done`, `t_audio_first_chunk`), stamped once each and carried. Never re-read the clock for the same instant.
- `worker.py` and the arq worker handle SIGINT and SIGTERM: drain, ack in flight, exit 0.
- Structured logs only. Never log a key, a token, or a connection string.

## v6 additions (plan §7.11–7.15)
- **New packages under `apps/api/daari/`**: `grounding/` (`verifier.py`, `evidence.py`, `nodata.py`), `intel/` (company+role question corpus), `prep/` (`notice.py`, `pack.py`, `schedule.py`), `schemes/telugu.py`, `personas/placement.py`. Routers add `prep`, `questions`, `evidence`.
- **Verified provider ids** (D9, re-verify at `/setup`, never from memory): Gemini `gemini-2.5-flash`; Groq chat `openai/gpt-oss-120b` (Llama 3.3/4 are **gone** from Groq); Groq ASR `whisper-large-v3` (+ `-turbo`); Ollama `llama3.1:8b` if pulled.
- **Verified endpoints** (D10): myscheme search `POST/GET https://api.myscheme.gov.in/search/v6/schemes` with `x-api-key`, browser UA and `Referer: https://www.myscheme.gov.in/` — **v4 and v5 now return 500**. Nominatim `search?format=jsonv2` with a contact UA, 1 req/s, cached. Remotive `https://remotive.com/api/remote-jobs`, no key. Adzuna `https://api.adzuna.com/v1/api/jobs/in/search/1`.
- **Grounding runs before rendering and before TTS.** `verifier.py`: sentence split → deterministic checks (`check_numbers`, `check_dates`, `check_names`, forbidden-claim regexes) → LLM SUPPORTED / UNSUPPORTED / NUMERIC-MISMATCH at temperature 0, cached → strike → citations. p95 budget 400 ms, checks run in parallel. Fewer than one surviving factual sentence → the no-data template. A struck sentence is **removed, not rephrased**.
- **Today's date is passed in the system prompt** and recall is forbidden. Every evidence item carries `fetched_at` and `as_of` where extractable; the reply states the newest evidence date it used.
- No personal names are stored from interview experiences or placement notices — strip spans before persisting.
