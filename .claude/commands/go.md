---
description: Run the next task in the current phase. `/go bug: <what you saw>` debugs instead.
---
1. Read `docs/STATE.md`, `git log --oneline -10`, and the current phase plan in `docs/superpowers/plans/`.
2. If the argument starts with `bug:` — run systematic-debugging on it first. Root cause, not symptom: grep every caller of the function before editing. Fix once, where all callers route through. Regression test that fails without the fix.
3. If no plan exists for the current phase, dispatch `planner` to write it (5 min brainstorm cap).
4. Pick the next unfinished task. Dispatch `builder` subagents — at most 3 in parallel, only on disjoint folders. Each writes findings incrementally to `.claude/state/`.
5. If the diff touches `router/`, `triage/guard.py`, `triage/ladder.py`, `constraints/`, or `vitals/detector.py` — dispatch `reviewer`. Fix every finding before continuing.
6. If the diff touches `apps/web/` — dispatch `designer` for the critique pass.
7. Run the full gate: `cd apps/api && uv run pytest -q`, `cd apps/web && pnpm test`, `uv run python ../../evals/run.py`. Show real output. A failing test is never skipped.
8. Conventional commit. Update `docs/STATE.md` AND `.claude/state/checkpoint.json` (task id, phase, files touched, commands + exit codes, evidence, single next action).
9. **Clock rule**: if this slot is past its §6 deadline, ship what passes, log what's missing in STATE.md, apply the §13 cut line, move on. Write the reason in `docs/DECISIONS.md`.

Print exactly five lines: done / verified how / running where / blockers / your to-do.
