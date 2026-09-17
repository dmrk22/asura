---
description: Run the next task in the current phase. `/go bug: <what you saw>` debugs instead.
---
1. Read `docs/STATE.md`, `git log --oneline -10`, and the current phase plan in `docs/superpowers/plans/`.
2. If the argument starts with `bug:` — run systematic-debugging on it first. Root cause, not symptom: grep every caller of the function before editing. Fix once, where all callers route through. Regression test that fails without the fix.
3. If no plan exists for the current phase, dispatch `planner` to write it (5 min brainstorm cap).
4. Pick the next unfinished task. Dispatch `builder` subagents — at most 3 in parallel, only on disjoint folders. Each writes findings incrementally to its own scratch file as it works, not only in its final reply — a stalled agent costs one re-dispatch, not the batch.
5. If the diff touches `packages/core/`, `agent/loop.py`, `schemes/extract_rules.py`, `interview/guard.py`, `voice/latency.py`, `grounding/verifier.py`, or `prep/notice.py` — dispatch `reviewer`. Fix every finding before continuing.
6. If the diff touches `apps/web/` — dispatch `designer` for the critique pass.
7. Run the full gate: `cd packages/core && uv run pytest -q`, `cd apps/api && uv run pytest -q`, `cd apps/web && pnpm test`, `cd apps/web && pnpm typecheck`, `uv run python evals/run.py` (includes `i18n_check.py`: zero missing `te` keys). Show real output. A failing test is never skipped.
8. Conventional commit. Update `docs/STATE.md` AND `.claude/state/checkpoint.json` (task id, phase, files touched, commands + exit codes, evidence, single next action).
9. **Clock rule**: if this slot is past the deadline in `docs/STATE.md`, ship what passes, log what's missing in STATE.md, apply the §13 cut line, move on. Write the reason in `docs/DECISIONS.md`.


10. **Grounding gate** (v6): if the diff can put prose on a screen, the reply path must run `grounding/verifier.py` and every factual sentence must carry a citation id. Uncited prose is a failing test, not a polish item.

Print exactly five lines: done / verified how / running where / blockers / your to-do.
