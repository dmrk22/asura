# STATE.md — DAARI (Team ASURA) · SYNORA Track 1 · Problem 01

Spec: `DAARI_BUILD_PLAN.md` **v6, 18 Sep 2026**. Build order + cut lines: §13. Repo layout: §6.
Updated 2026-09-18 by `/setup` (re-run against v6).

## Now
**P1 Skeleton + Constitution scaffold — done. The `/setup` exit criterion is met.**

P1 gate (§5.4, verbatim): *`http://localhost:8000/health` returns `{sha, db, redis, llm:[…], tools, asr: groq, tts: edge, adzuna, myscheme, nominatim, serpapi_budget_left}` and `http://localhost:3000` renders "DAARI · online" in en and te.*

Measured, not asserted:

| Probe | Live result |
|---|---|
| `db` | ok — Postgres 17.11, `vector` 0.8.6 created by the baseline migration |
| `redis` | ok — PONG |
| `llm` | gemini `gemini-2.5-flash` ok · groq `openai/gpt-oss-120b` ok · ollama **skipped, `model_not_pulled`** |
| `tools` | ok, count 0 — the registry is genuinely empty until P2 |
| `asr` | ok — groq `whisper-large-v3` |
| `tts` | ok — all three `edge-tts` voices present |
| `myscheme` · `nominatim` | ok — v6 endpoint, Guntur geocoded |
| `adzuna` | **error, http_401** — truncated key, human to-do 1 |
| `serpapi_budget_left` | **error, null** — truncated key, human to-do 1 |
| `ok` | `true` (gates on db + redis + tts + ≥ 1 llm) in 916 ms |

Web: bare `http://localhost:3000` → 307 → `/en` → **DAARI · online**; `/te` → **దారి · ఆన్‌లైన్** in Noto Serif/Sans Telugu, verified in a real browser and in the committed screenshots, not inferred from CSS. `pnpm build`, `pnpm typecheck` (TypeScript 7.0.2, no fallback needed) and `pnpm test` all green. Core 5 passed/1 skipped, api 6 passed, ruff and biome clean.

**Next: `/go`** — the planner writes `docs/superpowers/plans/phase-2-engine.md` from §13's P2 row (graph, vectors, matcher, roadmap + Before | After, CAT, tool registry), acceptance tests first.

## Phase status
No fixed clock slots in v6 — §13 gives the order, and the order holds for whatever time remains.

| Phase | Contents | Status |
|---|---|---|
| P1 | skeleton + Constitution scaffold | **done** |
| P2 | engine: graph, vectors, matcher, roadmap + Before \| After, CAT, tool registry | next |
| P3 | live leads + geocoding + demand + schemes pipeline + grounding verifier | not started |
| P4 | streaming voice + agent loop + i18n | not started |
| P5 | interview corpus + placement prep + coach | not started |
| P6 | evidence + polish | not started |
| P7 | rehearsal + audit | not started |
| — | freeze (`/ship`), optional deploy | not started |

## Done at this setup (v6 re-run)
- **Operating layer synced v5 → v6**: `CLAUDE.md` (13 non-negotiables, was 9 — adds the Constitution, "model memory is not a source", the te-key test, ToS); all five `.claude/rules/*.md` gained a v6 section (grounding, intel, prep, constitution, vectors, next-intl, new eval sets); `reviewer` now covers seven safety-critical modules; `red-team` has the six new v6 attacks; `/go`, `/demo`, `/audit` updated.
- **`docs/CONSTITUTION.md` written** — 13 articles, each with its enforcement point and the name of the test that will prove it. Status is public and honest: `scaffold` until the test is green.
- **P1 skeleton built and proven**: `packages/core` (purity + shared-engine AST tests, the latter proven against a deliberately violating fixture), `apps/api` (`/health`, baseline pgvector migration, config that cannot leak a key through repr/str), `apps/web` (tokens, next-intl en/te/hi, two unit tests each proven to fail on a real violation).
- **Agent frontmatter bug found and fixed** (D12): `tools: All tools` granted *zero* tools and every `builder`/`designer`/`red-team` dispatch was refused. Fixed by omitting the field. **Takes effect next `claude` start** — definitions are cached per session.
- **Subagent routing check: PASS** (D13) — both scaffold agents ran on `claude-sonnet-5`. `/model opusplan` is safe.
- **Live verification beat memory four times**: Groq has dropped Llama 3.3/4 → chain link is `openai/gpt-oss-120b` (D9); myscheme search is `v6`, v4/v5 return 500 (D10); `arq` forbids redis ≥ 6 → redis pinned 5.3.1 (D15); a reachable Ollama daemon with no model pulled is not a provider (D16).
- Hooks re-proven by execution: 20/20 sample payloads. MCP `context7` re-verified live. `.env.example` gained `DATAGOV_KEY` and the expected key lengths, so a truncated paste is self-evident next time.

## Blockers
1. **`ADZUNA_APP_KEY` and `SERPAPI_KEY` return 401.** Both are one character short (31 vs 32, 63 vs 64). Adzuna is *required* for demand weights, so this blocks **P3's** demand weighting; SerpAPI is cut line 8 and droppable. Neither blocks P2 — the engine takes demand as an argument.

## Phone / human to-do
1. **Re-paste two keys into `.env`** (Claude Code never edits `.env`). Copy the whole value — one lost character is the likely cause:
   - `ADZUNA_APP_KEY` — developer.adzuna.com → your app. **Expect 32 hex characters**; the current value is 31.
   - `SERPAPI_KEY` — serpapi.com/manage-api-key. **Expect 64 hex characters**; the current value is 63.
   Then `cd apps/api && uv run uvicorn daari.main:app --port 8000` and `curl -s localhost:8000/health | python3 -m json.tool` — those two fields should flip to `ok`.
2. **Install Microsoft Edge** — https://www.microsoft.com/edge. It is the demo browser: native `te-IN` voices are the TTS fallback if `edge-tts` fails mid-pitch.
3. **Restart Claude Code once** (`exit`, then `claude --model opus` → `/model opusplan`) so the fixed agent definitions load. Until then `builder`/`designer`/`red-team` dispatches are refused and `/go` falls back to generic agents.
4. **Optional, on home Wi-Fi with ≥ 16 GB RAM:** `ollama pull llama3.1:8b` — the third link in the provider chain, currently reported `model_not_pulled`.
5. **Test the wired mic in the hall.** Push-to-talk, 5 cm from the mouth — §16 still calls hall noise the largest residual risk.
6. **Bring one real placement notice** from the placement cell, names redacted (§4.6). P5's `/prep` beat is built around it.
7. **Telugu and Hindi review (data lane, §12)**: `దారి`, `దారి · ఆన్‌లైన్`, `భాష`, `DAARI · ऑनलाइन`, `भाषा` are LLM-written and unreviewed. They satisfy the key-parity test; they have not been read by a speaker.
8. **Optional deploy keys** (only if you want the QR): Supabase, Upstash, HF token. Deploy is cut line 14 — the laptop is the primary demo, and nothing was provisioned.

## Running where
- Postgres + Redis: `docker compose up -d` (both healthy, 5432 / 6379).
- Web dev server: **left running** on http://localhost:3000, log at `/tmp/daari-web-dev.log`.
- API: **not running** — `cd apps/api && uv run uvicorn daari.main:app --reload`.

## Next concrete action
`/go` — planner writes `docs/superpowers/plans/phase-2-engine.md` from §13's P2 row, acceptance tests first, then builders on disjoint engine modules.
