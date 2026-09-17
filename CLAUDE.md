# DAARI (Team ASURA) — rules for Claude Code

Hackathon: SYNORA Track 1, Problem 01. Spec = `DAARI_BUILD_PLAN.md` (v6, 18 Sep 2026). Read it, `docs/STATE.md` and `git log -10` at the start of every task.

## Non-negotiables
1. **One engine.** Both persona routes import `daari_core`. A test fails if `apps/api/daari/personas/*` contains matching, roadmap, eligibility, assessment, scam or scheduling logic, or if any route bypasses `daari_core`. `packages/core` never imports FastAPI, SQLAlchemy, httpx or any LLM client.
2. **No hardcoded leads or schemes.** Every job or scheme shown comes from a fetcher with `source_url` and `fetched_at`; the UI renders both. Only the registry of sources is configuration. Snapshots allowed only with the stamp visible.
3. **The LLM never decides.** Matching, roadmap, eligibility, ability estimate, scam score, distance, schedule and coverage stats are deterministic engine calls. The LLM orchestrates (tool calls), extracts structure at temperature 0 (cached by sha256), and writes words. Every tool call is logged to the agent trace.
4. **Feedback guard.** Every interview feedback item carries a verbatim quote from the transcript. Praise without a quote is rejected. Adversarial violations = 0.
5. **Versions, model IDs and free-tier limits verified** (Context7 / `npm view` / PyPI / provider consoles) before use. Never from memory. See `docs/DECISIONS.md` D3, D9, D10.
6. **₹0.** No paid API, no card, no paid tier. SerpAPI's 100/month is a budget: rehearsal + demo only, cached.
7. **The scripted demo path works with the network unplugged**: cached LLM/tool responses, cached ASR for rehearsed clips, pre-rendered TTS, snapshot leads and schemes with stamps, local DB and Redis.
8. **Synthetic personas only.** Real live leads and schemes, fake people.
9. **Clock rule.** At each phase deadline, ship what passes tests, log what's missing in `docs/STATE.md`, move on. Cut lines (§13) fall back per engine. Never extend a slot without a `docs/DECISIONS.md` entry.
10. **The Constitution** (`docs/CONSTITUTION.md`) is enforced in code: every user-facing factual sentence passes `grounding/verifier.py`; every number passes `constitution.check_numbers()`; every date passes `check_dates()`. A sentence that fails is **removed, not rephrased**. The "no data" template is a success path.
11. **Model memory is not a source.** Anything time-bound (jobs, schemes, questions, companies, dates, salaries, deadlines, eligibility) is answered only from an evidence bundle with `fetched_at` stamps. The system prompt states today's date and forbids recall.
12. **Every screen and every string has en / te / hi entries** in `apps/web/messages/*.json`; a test fails on a missing `te` key. Scheme and job summaries shown in Telugu are generated at temperature 0 from the English evidence and never add an entity or a number (diff test).
13. **ToS is law.** Sources whose ToS forbid scraping are never fetched (Glassdoor). Polite limits (1 req/s), caching, no personal names stored from interview experiences or notices.

## Skills
brainstorming (5 min max per phase) → writing-plans → subagent-driven-development → test-driven-development → systematic-debugging → verification-before-completion. karpathy-guidelines on every diff. frontend-design + design-critique on every UI task; `docs/UI_BRIEF.md` is law.

## Process budget
Full reviewer pass only for `packages/core/`, `agent/loop.py`, `schemes/extract_rules.py`, `grounding/verifier.py`, `interview/guard.py`, `voice/latency.py`, `prep/notice.py`. Everything else: builder self-review + tests. One-page plans per phase. Up to three builders in parallel on disjoint folders.

## Commands
- core: `cd packages/core && uv run pytest -q`
- api: `cd apps/api && uv run pytest -q` · `uv run alembic revision --autogenerate -m "<msg>" && uv run alembic upgrade head` · `uv run uvicorn daari.main:app --reload` · `uv run arq daari.workers.WorkerSettings`
- web: `cd apps/web && pnpm dev | pnpm build | pnpm test | pnpm e2e`
- infra: `docker compose up -d` · evals: `uv run python evals/run.py`

## Models
Aliases on the Anthropic API: `opus` = Opus 5, `sonnet` = Sonnet 5, `haiku` = Haiku 4.5. Never pin version strings here.
- `/setup` runs in a session started with `claude --model opus`. After the green health check the human switches to `/model opusplan`.
- Subagent frontmatter: planner opus · builder sonnet · reviewer opus · designer sonnet · red-team opus. Effort default (high) everywhere.
- Routing check: `/setup` dispatches a builder and greps its transcript under `~/.claude/projects/<proj>/<session>/subagents/` for "model". If not sonnet: unset `CLAUDE_CODE_SUBAGENT_MODEL` (never set it to `inherit`), restart, re-check; if it still fails, note in `docs/DECISIONS.md` and continue on opusplan.
- If plan limits bite: `/model sonnet`, all agents sonnet.
- **Product LLM chain** (not Claude): Gemini `gemini-2.5-flash` → Groq `openai/gpt-oss-120b` → Ollama `llama3.1:8b` → cache. Groq no longer serves Llama 3.3/4 (D9).

## Compaction policy
Preserve: current phase + task, failing tests, open decisions, human to-do. Re-read `docs/STATE.md` after compaction.

## Never
`push --force` · recursive force-delete outside build dirs · edit or print `.env` · skip a failing test · hardcode a lead or a scheme · put engine logic outside `packages/core` · let the LLM return a match/score/eligibility directly · state a fact with no evidence id · purple/violet/navy hues · gradients on product screens · any paid service.
