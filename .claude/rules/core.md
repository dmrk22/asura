# core.md — packages/core (`daari_core`)

This is the shared engine. Both persona routes import it; nothing else may hold this logic.

- **Pure.** `daari_core` imports numpy, networkx and the stdlib. It never imports FastAPI, SQLAlchemy, httpx, redis or any LLM client. A test asserts the import graph.
- **Deterministic.** No clock reads, no randomness, no network, no I/O in `match`, `roadmap`, `eligibility`, `assess`, `scam` or `interview_metrics`. Seed anything stochastic explicitly and take the seed as an argument.
- **One clock per measurement.** Timestamps are stamped once by the caller and carried; never re-read the clock and call it the same instant.
- The AST test in `packages/core/tests/` fails if matching, roadmap, eligibility, assessment or scam logic appears under `apps/api/daari/personas/`, or if either persona route reaches a result without calling `daari_core`.
- **Invariants that hypothesis must hold** (§7.3, §7.5):
  - Learning a required skill never lengthens the roadmap.
  - A demand increase for a skill never moves that skill later in the path.
  - `diff(x, x)` is empty.
  - Both persona adapters produce identical output for identical inputs.
  - Rasch: SE decreases monotonically; an all-correct respondent ends at θ ≥ +1; the stopping rule always terminates (SE < 0.4 or 6 items).
  - `evaluate()` is idempotent; `Unknown` never collapses to `qualifies`.
- **Every score is decomposed.** `match()` returns the component breakdown (`coverage`, `gap_cost`, `constraint_fit`, `demand_bonus`), not just a number. The UI renders the breakdown.
- **Scam scoring is rules-first** (`scam.py`, §7.4). The LLM second opinion lives in `apps/api` and may add at most 0.2, with a quoted reason.
- `telemetry.py` counts calls per persona. Those counters are what `/evidence` shows; they are read from the live process, never hardcoded.
- Tests: `cd packages/core && uv run pytest -q`. Every fix gets a regression test that fails without it.
