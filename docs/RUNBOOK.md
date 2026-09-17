# RUNBOOK — start DAARI from cold

Written 2026-09-18 04:15. If you are reading this at 5am with no context, start here.

## The 30-second version

```bash
cd ~/dev/asura/apps/api
uv run uvicorn daari.main:app --port 8000 --reload
```

**If that says "address already in use":** the older standalone `demo/backend`
is probably still on :8000 from a previous session. Two choices — pick one and
stick to it for the pitch:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN          # see what is holding it
pkill -f "uvicorn app.main:app"            # stop the old demo backend, then retry
```

or just run the real API somewhere else and use that port everywhere:

```bash
uv run uvicorn daari.main:app --port 8010 --reload
```

The old `demo/backend` and this API are **different services with different
route shapes** (`/profiles` and `/jobs` there, `/personas` and `/match` here).
`demo/frontend/index.html` calls the old one. Do not point it at this API
without changing its fetch paths.

Then open http://localhost:8000/docs — FastAPI's interactive docs. Every engine
route is there with a **Try it out** button. That is a working backend you can
demo from the browser with no frontend at all.

**The engine routes do not need Postgres, Redis, the network, or any API key.**
They read the committed taxonomy from `data/` and run pure Python. Only
`/health` touches the database and the providers. If everything else is on
fire, the engine still answers.

## If you want /health green too

```bash
cd ~/dev/asura
docker compose up -d          # postgres + redis, ~10s
cd apps/api && uv run alembic upgrade head
```

`/health` gates on db + redis + tts + at least one LLM. `adzuna` and
`serpapi_budget_left` are expected to read `http_401` until the two truncated
keys in `.env` are re-pasted — that does not make `ok` false.

## The routes

| Route | What it does |
|---|---|
| `GET /taxonomy` | 24 skills, 2 roles, every node with its real source and te/hi labels |
| `GET /personas` | Ravi (rural), Priya (student), blank — all synthetic |
| `POST /roadmap` | `{held, goal, demand?, persona?}` → ordered steps, hours, weeks, `why` per step |
| `POST /roadmap/learn` | `{held, goal, skill, level}` → **before, after and the diff** (`cause: learner`) |
| `POST /roadmap/shock` | `{held, goal, skill, weight}` → the Market shock beat (`cause: market`) |
| `POST /match` | `{held, districts?, demand?}` → ranked listings with all four score components |
| `GET /evidence` | live per-persona call counters against the one `daari_core` |
| `GET /health` | the P1 probe board |

## Four curls that are the demo

```bash
API=http://localhost:8000
PRIYA='{"spoken_english":3,"basic_numeracy":3,"digital_literacy":3,"python_programming":2,"sql_querying":2}'

# 1. Priya's roadmap: 310h, 31 weeks, 10 steps
curl -s $API/roadmap -H 'content-type: application/json' \
  -d "{\"held\":$PRIYA,\"goal\":\"data_analyst\",\"persona\":\"student\"}"

# 2. "I learned SQL" -> 310h becomes 270h, cause=learner
curl -s $API/roadmap/learn -H 'content-type: application/json' \
  -d "{\"held\":$PRIYA,\"goal\":\"data_analyst\",\"skill\":\"sql_querying\",\"level\":5}"

# 3. Market shock on Python -> moves from step 13 to step 7, cause=market
curl -s $API/roadmap/shock -H 'content-type: application/json' \
  -d '{"held":{},"goal":"data_analyst","skill":"python_programming","weight":2.0}'

# 4. Ravi, the rural persona, same engine
curl -s $API/match -H 'content-type: application/json' \
  -d '{"held":{"two_wheeler_riding":3},"districts":["Guntur"],"persona":"rural"}'
```

Pipe any of them through `python3 -m json.tool` to read them on stage.

## Numbers you can quote (measured 2026-09-18, not estimated)

- Priya → Data Analyst: **310 h, 31 weeks at 10 h/wk**, 10 steps.
- Ravi → Delivery Executive: **150 h, 15 weeks**, 14 steps.
- "I learned SQL": 310 h → **270 h**, `removed: [sql_querying]`, `cause: learner`.
- Market shock on Python: requested 50× → **applied 2.0×** (clamped, and the
  response says both numbers). Python moves step **13 → 7**. `hours_delta: 0`.
- `/evidence`: both `student` and `rural` counters non-zero against one `daari_core`.

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
available to learn. A roadmap that put Power BI before SQL would be worse than
useless. `test_prerequisites_outrank_demand` pins that.

**"You asked for 50× and applied 2×?"** Yes, and the response says so.
§7.3 caps the demand multiplier at 2× so one hot skill cannot dominate. We show
`requested_weight` and `applied_weight` rather than implying the 50× landed.

**"Are these real jobs?"** No, and we say so in the response: `live: false`,
every card stamped `source: seed`, `is_live: false`, with a `provenance_note`.
The live fetchers are P3. We would rather show a seed and say it than show a
seed and imply it is live.

## Known rough edge

Priya's top match is **Store Cashier at 25 % coverage** — truthful (she has the
numeracy) but odd at the head of a data-analyst's list. Cause: the seed
listings' `required_skills` levels were copied from each skill node's own level
instead of being set per listing. It is a data fix, not a scorer fix. See
`docs/DECISIONS.md` D19.

## Not built yet

`assess.py` (Rasch CAT), `demand.py` (PMI from live listings), `eligibility.py`,
`scam.py`, the agent tool registry, the live fetchers, voice, interview.
The `demand` input is plumbed end to end and honoured — nothing computes it
from real listings yet.

## Gate

```bash
cd packages/core && uv run pytest -q && uv run ruff check .
cd ../../apps/api  && uv run pytest -q && uv run ruff check .
```
Last green run: core 63 passed / 1 skipped, api 25 passed, ruff clean both.
