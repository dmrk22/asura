# STATE.md — NADI (Team ASURA)

**Updated:** 17 Sep 2026, setup complete · **Phase:** P1 Skeleton — not started · **Clock:** not started

## Now
**P1 Skeleton (0:00–0:45).** First task: `llm/` provider chain — `complete()` / `vision()` with
Gemini → Groq → Ollama → cache, per-provider circuit breaker, token bucket, sha256 response cache.
Everything else in P1's gate is already standing (see Done).

Run `/go` to start. It reads this file, the phase plan and `git log -10` first.

## Done at setup (verified, not assumed)
| Thing | Evidence |
|---|---|
| Repo scaffold §4 | 58 files; `apps/api`, `apps/web`, `data/`, `evals/`, `scripts/`, `.claude/`, `docs/` |
| Postgres 17 + pgvector | container healthy; `CREATE EXTENSION vector` → **0.8.6** |
| Redis 7 | container healthy; `redis-cli ping` → PONG |
| Alembic baseline | `alembic upgrade head` applied; `alembic_version` = `36c6c9f06d27` |
| API `/health` | live server returned `{"sha":...,"db":"ok","redis":"ok","llm":["cache"]}` |
| Web renders | `pnpm build` clean; served page contains **NADI · online** |
| Full gate | biome 0 · tsc 0 · next build 0 · ruff 0 · pyright 0 · pytest 0 |
| Hooks | 14/14 cases pass — force-push blocked, `rm -rf` outside build dirs blocked, `.env` reads blocked |
| Slash commands | `/go /lane /demo /audit /ship` registered and listed by the harness |
| MCP | Context7 answered a live query; Playwright available via plugin |
| Versions | pinned from the registry at setup, not memory — see DECISIONS.md |
| CI on GitHub | run 35235735902 on `main` — **web ✓ api ✓ evals ✓** |
| Repo | github.com/dmrk22/asura (private), `main` pushed |

`llm` shows only `cache` because `.env` does not exist yet. It will list `gemini` / `groq` once keys are in.

## Blockers
**None for P1 code.** The LLM chain can be built and unit-tested against the cache tier with no keys.
Keys are needed before the first real vision call (P6 Meals) and the router tie-break (P2).

## Phone / human to-do
1. **`.env` — do this first.** `cp .env.example .env`, then fill **at least one**:
   - `GEMINI_API_KEY` — aistudio.google.com → *Get API key*. No card.
   - `GROQ_API_KEY` — console.groq.com → *API keys*. No card.
   While there, note the free-tier **requests-per-minute** for each and tell me — they go into
   `nadi/config.py` (`gemini_rpm`, `groq_rpm`) so the token bucket uses a real number, not my placeholder
   (currently 10 and 30). Never paste a key into chat; the file is enough. I never read or edit `.env`.
2. **Ollama models — home Wi-Fi only, ~9 GB.** This Mac has 16 GB RAM, so it qualifies. `ollama list` is
   currently empty. Run: `ollama pull qwen2.5vl:7b && ollama pull llama3.1:8b`.
   Skip it and the chain simply falls through to the cache — the scripted demo still works offline.
3. **Food photos at lunch.** 8 canteen plates (thali, dal-rice, roti-sabzi, idli-sambar, dosa, biryani,
   curd rice, samosa + chai). Note the contents and counts (2 rotis, 1 katori dal). Into
   `evals/meals/photos/` when P6 asks. This is both the macro eval set and the demo images.
4. **Teammate laptops** (if a second one joins): `git clone`, then install the same plugins —
   superpowers, frontend-design, karpathy-guidelines. `.mcp.json` brings Context7 and Playwright along
   with the clone. Then `/lane api|web|data`. Nobody edits another lane's folder.
5. **Optional, deploy only (hour 11:30 — skip unless the clock is kind).** I cannot do these: both CLIs
   are missing and both need an interactive browser login.
   `pnpm add -g vercel && vercel login` · `uv tool install huggingface_hub && hf auth login` ·
   Supabase project `asura-nadi` (Singapore) → pooler string → `PROD_DATABASE_URL` ·
   Upstash Redis (Singapore) → `PROD_REDIS_URL` · HF write token → `HF_TOKEN`.
   All four blank = `/ship` skips deploy and the laptop demo stands alone. That is a fine outcome.

## Next concrete action
`/go` → dispatch `planner` for `docs/superpowers/plans/phase-1-skeleton.md`, then build `nadi/llm/`.
