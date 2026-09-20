# STATE.md — DAARI (Team ASURA) · SYNORA Track 1 · Problem 01

Spec: `DAARI_BUILD_PLAN.md` **v6, 18 Sep 2026**. Build order + cut lines: §13. Repo layout: §6.
Updated 2026-09-18 by `/setup` (re-run against v6).

## Now — the demo is retired, the real stack is the product

**Plan:** `~/.claude/plans/now-keep-the-demo-foamy-sifakis.md`, executed in full (GO 1 + GO 2).
**Not yet committed** — working tree only, per the standing rule (commit/push only on request).
Everything below was measured against a running server, not asserted.

**Repair audit — 2026-09-20:** core (125 passed, 1 skipped) and API (48
passed) test/lint suites are green. The web app now self-hosts its committed
font assets, including Hindi's Noto Sans Devanagari, so it no longer requires
Google Fonts while building or in the unplugged demo. `pnpm build` uses Next's
webpack mode: Turbopack repeatedly stalled before compilation on this host,
while webpack completed the identical production build. Web typecheck, lint,
unit tests, and that production build are green under Node 22 LTS.

### What's real and live now

| Engine (`packages/core/daari_core/`) | Proof |
|---|---|
| `scam.py` — rules-first Scam Shield, 6 weighted rules, every reason a quoted substring | 125 core tests; **live catch**: a real Remotive listing ("Inside Sales Contractor", OTE $25k–$35k) scored 0.40/`check` with quoted reasons `pay_out_of_band: "25"`, `urgency_no_interview: "unlimited earning"` — screenshotted at `apps/web/tests/screenshots/leads-live-on-en-1440.png` |
| `eligibility.py` — 3-state Kleene evaluator, `unknown` never collapses to qualifies | hypothesis + exhaustive Kleene-table tests |
| `geo.py` — haversine | tested against known city pairs |
| `assess.py` — 1PL Rasch CAT (`start`/`next_item`/`update`/`should_stop`) | hypothesis: SE non-increasing, all-correct → θ≥+1, always terminates ≤6 items; **live 6-item loop run against the server**, SE fell 1.414→0.768, hard-stopped at item 6 |

| API (`apps/api/daari/`) | Proof |
|---|---|
| `llm/chain.py` — Gemini→Groq→Ollama→cache, sha256-cached, circuit breaker, structlog | `/health` shows gemini + groq `ok` |
| `fetchers/{remotive,adzuna,myscheme,nominatim}.py` | **live**: real Adzuna/Remotive jobs, real myscheme.gov.in schemes (KALIA, POMIS, …), real Nominatim geocode for Guntur — all via `GET /leads/live`, `GET /schemes`, `GET /geocode` |
| `POST /match` `live: bool` | merges live + seed, reports `live_count`/`seed_count`/`live_errors`, every card carries a `scam` verdict |
| `POST /assess/next`, `POST /assess/answer` | stateless CAT over the real 26-item bank (`data/items/items.yaml`), server-side grading, never leaks the answer |
| `data/sources.yaml` | the one place a source is named; myscheme's public `x-api-key` lives here for the fetcher (note: `main.py:39`'s `/health` probe keeps its own copy of the same public key for its liveness check — duplicated, not a secret, not consolidated this hour) |

| Web (`apps/web/`) — **the Next app is the product now, not a wordmark** | Proof |
|---|---|
| `/onboard`, `/path`, `/leads`, `/evidence` | pnpm typecheck/lint/test/build all green; screenshots in `apps/web/tests/screenshots/` at 1440px + 390px, en + te, incl. the live-scam catch above |
| `/path` | real d3-force graph, Before\|After panes for both "Simulate skill update" and "Market shock", **shows `requested_weight` vs `applied_weight`** (the 50×→2× clamp) |
| `/leads` | live-listings toggle, match% + full component breakdown, amber missing-skill chips, ScamBadge (renders nothing when clear — a badge without reasons is a bug), `source`+`fetched_at` in mono on every card, `safeHref()` guards against a non-http(s) `source_url` |
| i18n | en/te/hi key parity enforced by test; Telugu/Hindi hand-translated, not machine-copied |

**Adzuna key**: was 401 at session start (truncated paste); human re-pasted it mid-session; `/health` now reports `adzuna: ok` and `/leads/live` returns real Adzuna listings.

**Security findings from the background reviewer, fixed in-session:**
1. `fetchers/adzuna.py` was about to leak the credentialed request URL into the public `source_url` field and hand-concatenate its query string. Fixed: `source_url` is always Adzuna's own `redirect_url` or a credential-free public search link; requests use `httpx params=`. Regression tests added.
2. `apps/web` leads page rendered a fetcher-sourced `source_url` straight into `<a href>` (a `javascript:` XSS vector). Fixed with `safeHref()` — non-http(s) URLs render as plain text, never a link.

### Product extension — 2026-09-20
- **User-facing flows now exist** for `/assess`, `/schemes`, `/voice`, `/interview`, and `/prep`, in en/te/hi. The CAT is server-graded, scheme cards retain their live source/fetch stamp, browser voice uses the Web Speech API plus local speech synthesis, interview feedback is quote-bound to the candidate transcript, and placement prep schedules from a user-confirmed notice URL and date.
- **Eligibility is intentionally still three-valued.** A live scheme with no reviewed predicate AST returns `unknown` and explains that rule extraction is required; it never says a person qualifies. `extract_rules.py` is the remaining pipeline join.
- The browser voice surface is a functional zero-cost fallback, not the planned server-streamed Groq/edge-tts pipeline. Interview company-corpus ingestion, document parsing, live-demand calculation, server agent orchestration/trace persistence, grounding verifier, and SerpAPI remain future backend work.
- `demo/` was **retired from running** (its two processes on :3000/:8000 killed, `.claude/launch.json` repointed at the real stack) but the directory itself was left on disk, unserved — deleting it wasn't this hour's risk to take.

### How to run it
```
cd apps/api && uv run uvicorn daari.main:app --port 8000 --reload   # real engine, real fetchers
cd apps/web && pnpm dev --port 3000                                  # real product
```
Both were left running on their standard ports at the end of this session.

---

**P2 partial — the backend serves the real engine. Roadmap, Before | After, Market shock and the matcher are live over HTTP.**

Added 2026-09-18 ~04:00, after the remote was found to be 9 commits stale (see below):

| What | Where | Proven by |
|---|---|---|
| `roadmap.compute` + `diff` — demand-weighted priority-queue Kahn | `packages/core/daari_core/roadmap.py` | 18 tests incl. the three §7.3 invariants as hypothesis properties |
| `match` — level-aware coverage, closure gap cost, all four components returned | `packages/core/daari_core/match.py` | 21 tests |
| `GET /taxonomy`, `GET /personas`, `POST /roadmap`, `POST /roadmap/learn`, `POST /roadmap/shock`, `POST /match`, `GET /evidence` | `apps/api/daari/routes.py` | 19 route tests + a live smoke against a running server |
| Seed listings + personas as **stamped data, not code literals** | `data/leads/seed_jobs.yaml`, `data/personas/personas.yaml` | every card carries `source`/`source_url`/`fetched_at`/`is_live:false` |

Gate run 2026-09-18: **core 63 passed / 1 skipped · api 25 passed · ruff clean both.**

Live numbers from a running server (not asserted — measured):
- Priya → Data Analyst: **310 h, 31 weeks at 10 h/wk**, 10 steps.
- Ravi → Delivery Executive: **150 h, 15 weeks**, 14 steps.
- "I learned SQL" → 310 h → 270 h, `cause: learner`, `removed: [sql_querying]`.
- Market shock on Python at a requested 50× → **applied 2.0× (clamped, and the response says so)**; Python moves 13 → 7, `cause: market`, `hours_delta: 0`.
- `/evidence` shows both personas' counters moving against one `daari_core`.

**Open — needs a human call (see DECISIONS D19):** the §7.2 additive formula let a 0 %-coverage nearby listing top Priya's matches. Fixed with a *relevance floor* (a zero-coverage candidate never outranks a positive-coverage one); the published weights are untouched. Priya's top match is now Store Cashier at 25 % coverage — honest, but it is a retail job heading a data-analyst's list. If that reads badly on stage, the fix is better seed listings or level-aware job requirements, not a re-weighting.

**Still not built (P2 remainder):** `assess.py` (Rasch CAT), `demand.py` (PMI from live listings), `eligibility.py`, `scam.py`, the tool registry, and the live fetchers. The demand input exists and is honoured end to end; nothing computes it from real listings yet.

---

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
