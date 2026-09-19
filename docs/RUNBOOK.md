# RUNBOOK — start DAARI from cold

Written 2026-09-18 04:15, rewritten 2026-09-18 ~05:xx after retiring the standalone HTML demo
(D21) and wiring scam/eligibility/assess + live fetchers into the real stack. If you are reading
this at 5am with no context, start here.

## The 30-second version

```bash
cd ~/dev/asura/apps/api && uv run uvicorn daari.main:app --port 8000 --reload
cd ~/dev/asura/apps/web && pnpm dev --port 3000
```

Open **http://localhost:3000/en/onboard** — that's the real product now: pick Priya or Ravi,
then `/path`, `/leads`, `/evidence`. Or open http://localhost:8000/docs for FastAPI's interactive
docs with a **Try it out** button on every route — a working backend with no frontend at all.

**There is no more port collision.** The old `demo/backend` (:8000) and `demo/frontend` (:3000,
via `python3 -m http.server`) were killed and retired this session (D21) — `.claude/launch.json`
now points at the real API and `pnpm dev`. `demo/` is still on disk but nothing serves it.

**The engine routes do not need Postgres, Redis, the network, or any API key.** They read the
committed taxonomy from `data/` and run pure Python. Only `/health` and the live-fetcher routes
(`/leads/live`, `/schemes`, `/geocode`, `/match` with `live=true`) touch the network.

## If you want /health green too

```bash
cd ~/dev/asura
docker compose up -d          # postgres + redis, ~10s
cd apps/api && uv run alembic upgrade head
```

`/health` gates on db + redis + tts + at least one LLM. `adzuna` was `http_401` (a truncated
key paste) — **fixed this session**, now reports `ok`. `serpapi_budget_left` may still read
`http_401`; SerpAPI is cut line 8, droppable, and nothing depends on it.

## The routes

| Route | What it does |
|---|---|
| `GET /taxonomy` | 24 skills, 2 roles, every node with its real source and te/hi labels |
| `GET /personas` | Ravi (rural), Priya (student), blank — all synthetic |
| `POST /roadmap` | `{held, goal, demand?, persona?}` → ordered steps, hours, weeks, `why` per step |
| `POST /roadmap/learn` | `{held, goal, skill, level}` → **before, after and the diff** (`cause: learner`) |
| `POST /roadmap/shock` | `{held, goal, skill, weight}` → the Market shock beat (`cause: market`), `requested_weight` vs `applied_weight` |
| `POST /match` | `{held, districts?, demand?, live?}` → ranked listings, all four score components, a Scam Shield verdict on every card, `live_count`/`seed_count`/`live_errors` when `live: true` |
| `GET /leads/live?q=&limit=` | live Remotive + Adzuna listings, mapped through `skills_map`, same card shape as `/match` (incl. `scam`) |
| `GET /schemes?q=&limit=` | live myscheme.gov.in search, stamped `source`/`source_url`/`fetched_at` |
| `GET /geocode?q=` | live Nominatim geocode, one place name |
| `POST /assess/next` | `{state?, skill_id?}` → the next CAT item at max Fisher information, or `done: true`. Never returns the item's answer. |
| `POST /assess/answer` | `{state, item_id, given_answer}` → graded server-side against the item bank, returns updated `theta`/`se` |
| `GET /evidence` | live per-persona call counters against the one `daari_core` |
| `GET /health` | the P1 probe board |

## Curls that are the demo

```bash
API=http://localhost:8000
PRIYA='{"spoken_english":3,"basic_numeracy":3,"digital_literacy":3,"python_programming":2,"sql_querying":2}'

# 1. Priya's roadmap: 310h, 31 weeks, 10 steps
curl -s $API/roadmap -H 'content-type: application/json' \
  -d "{\"held\":$PRIYA,\"goal\":\"data_analyst\",\"persona\":\"student\"}"

# 2. "I learned SQL" -> 310h becomes 270h, cause=learner
curl -s $API/roadmap/learn -H 'content-type: application/json' \
  -d "{\"held\":$PRIYA,\"goal\":\"data_analyst\",\"skill\":\"sql_querying\",\"level\":5}"

# 3. Market shock on Python -> moves from step 13 to step 7, cause=market, 50x clamped to 2x
curl -s $API/roadmap/shock -H 'content-type: application/json' \
  -d '{"held":{},"goal":"data_analyst","skill":"python_programming","weight":50}'

# 4. Ravi, live listings merged with seed, every card scored for scam
curl -s $API/match -H 'content-type: application/json' \
  -d '{"held":{"two_wheeler_riding":3},"districts":["Guntur"],"persona":"rural","live":true}'

# 5. Real jobs, no key needed for Remotive
curl -s "$API/leads/live?q=data%20analyst&limit=3"

# 6. Real schemes from myscheme.gov.in
curl -s "$API/schemes?q=income&limit=3"

# 7. Real geocode
curl -s "$API/geocode?q=Guntur"

# 8. A CAT item — note "answer" is never in the response
curl -s $API/assess/next -H 'content-type: application/json' -d '{"skill_id":"sql_querying"}'
```

Pipe any of them through `python3 -m json.tool` to read them on stage.

## Numbers you can quote (measured 2026-09-18, not estimated)

- Priya → Data Analyst: **310 h, 31 weeks at 10 h/wk**, 10 steps.
- Ravi → Delivery Executive: **150 h, 15 weeks**, 14 steps.
- "I learned SQL": 310 h → **270 h**, `removed: [sql_querying]`, `cause: learner`.
- Market shock on Python: requested 50× → **applied 2.0×** (clamped, and the
  response says both numbers). Python moves step **13 → 7**. `hours_delta: 0`.
- `/evidence`: both `student` and `rural` counters non-zero against one `daari_core`.
- **Live**, this session: a real Remotive listing ("Inside Sales Contractor", Credit Wellness
  LLC, OTE $25k–$35k) scored **0.40 / "check this"** by the Scam Shield, reasons
  `pay_out_of_band: "25"` and `urgency_no_interview: "unlimited earning"` — screenshot at
  `apps/web/tests/screenshots/leads-live-on-en-1440.png`.
- **Live**, this session: a full 6-item CAT run on `sql_querying` (all wrong) — SE fell
  1.4142 → 0.7680, theta -2.007, hard-stopped at item 6 exactly as the invariant requires.
- **Live**, this session: `POST /match {live:true}` on Ravi's held skills → `live_count: 8,
  seed_count: 10` — Adzuna and Remotive listings genuinely merged and ranked by the unmodified
  `daari_core.match`.

## Answers to the questions a judge will actually ask

**"Is the engine really shared?"** `packages/core/daari_core/` is imported by
both persona paths; `apps/api/daari/routes.py` has no persona branch; the AST
test in `packages/core/tests/test_shared_engine.py` fails if matching or roadmap
logic appears outside core. `/evidence` shows both personas' counters moving.

**"Is the roadmap really adaptive?"** Two different causes, both computed:
`cause: learner` when the profile changes, `cause: market` when demand does.
The diff is computed from two real paths, not scripted.

**"Why is Power BI not first when I shock it?"** Because `data_cleaning` and
`sql_querying` gate it. Demand reorders only among skills that are actually
available to learn. `test_prerequisites_outrank_demand` pins that.

**"You asked for 50× and applied 2×?"** Yes, and the response says so.
§7.3 caps the demand multiplier at 2× so one hot skill cannot dominate. We show
`requested_weight` and `applied_weight` rather than implying the 50× landed.

**"Are these real jobs?"** They can be, now — pass `live: true` to `POST /match` or hit
`GET /leads/live`. Every live card is stamped `is_live: true`, `source: adzuna|remotive`,
a real `source_url`, a real `fetched_at`. Seed listings still exist and are honestly stamped
`source: seed`, `is_live: false` — the two are merged, never confused.

**"How does the Scam Shield actually work?"** `daari_core.scam.score()` — six deterministic
rules over the listing's own text (upfront fees, personal-contact-only, no org, pay out of band,
unverifiable url, urgency-with-no-interview), each contributing a weight and a **quoted
substring** of the listing that triggered it. `>= 0.5` red, `>= 0.3` amber, else clear — never a
silent block. It caught a real live listing this session (see above); the LLM never touches this
score.

**"What about eligibility for schemes — does an LLM decide who qualifies?"** No.
`daari_core.eligibility.evaluate()` is a pure three-valued (true/false/unknown) evaluator over a
predicate AST; `unknown` never renders as qualifying. **Honest gap:** nothing extracts that AST
from a live scheme's text yet (`schemes/extract_rules.py`, an LLM-at-temperature-0 step, was cut
this session — D23) so there is no `/schemes` eligibility screen yet, only the tested, live-proven
`GET /schemes` search and the tested, live-proven `eligibility.evaluate()` engine, not yet joined.

**"Is the CAT assessment real IRT?"** Yes — 1PL Rasch, max-Fisher-information item selection,
Newton-Raphson theta update, SE-based stopping (`SE < 0.4` or 6 items, whichever first). Proven
with hypothesis properties and a live 6-item run (numbers above). **Honest gap:** no `/assess`
screen yet — the routes are real and curl-able, nobody has wrapped them in UI.

## Known rough edge

Priya's top *seed-only* match is **Store Cashier at 25 % coverage** — truthful (she has the
numeracy) but odd at the head of a data-analyst's list. Cause: the seed listings'
`required_skills` levels were copied from each skill node's own level instead of being set per
listing. It is a data fix, not a scorer fix. See `docs/DECISIONS.md` D19. With `live: true` this
is now diluted by real Adzuna/Remotive data analyst roles ranking above it.

## Not built yet (say so, don't hide it)

- No `/assess` or `/schemes` UI screens (engines + routes are real and live-verified; not wrapped
  in a screen — the single biggest remaining gap).
- `schemes/extract_rules.py` (LLM → predicate AST for `eligibility.evaluate()`) — cut this
  session, D23.
- Voice/ASR/TTS, `/ws/voice`, interview coach + feedback guard, prep-from-notice, the agent trace
  drawer UI, the grounding verifier's LLM pass, SerpAPI, `demand.py` (PMI from live listings) —
  unchanged from before, still not built.
- `demand` is plumbed end to end and honoured by the engine; nothing computes it from real
  listings automatically yet — it's still a caller-supplied input.

## Gate

```bash
cd packages/core && uv run pytest -q && uv run ruff check .
cd ../../apps/api  && uv run pytest -q && uv run ruff check .
cd ../web && pnpm typecheck && pnpm lint && pnpm test && pnpm build
```
Last green run (2026-09-18, this session): **core 125 passed / 1 skipped · api 48 passed · ruff
clean both · web typecheck/lint/test/build all green.**
