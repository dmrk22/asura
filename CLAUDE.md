# NADI (Team ASURA) — rules for Claude Code

Hackathon: SYNORA Track 1, Problem 02. 12 hours. Spec = `NADI_BUILD_PLAN.md`.
Read the spec, `docs/STATE.md` and `git log -10` at the start of every task.

## Non-negotiables
1. Safety engine first: red-flag recall = 100%, adversarial-diagnosis violations = 0. CI fails otherwise. No feature merges over a red safety eval.
2. Deterministic where the rubric says deterministic: router tiers 1–2 use fixed seeds and frozen embeddings; tier 3 runs at temperature 0, cached by sha256(input), logged with its reason.
3. Every wellness output passes `constraints.engine.enforce()` and carries a trace. No bypass flag exists.
4. Anything derived from an image is shown as a range with confidence, never a point.
5. Library versions, model IDs and free-tier limits are verified against current docs (Context7 / `npm view` / PyPI / provider consoles) before use. Never typed from memory.
6. ₹0: no paid API, no card, no paid tier. If a provider needs a card, it is the wrong provider.
7. The scripted demo path works with the network unplugged (cached LLM responses, local DB, local Redis, local models if pulled).
8. Synthetic personas only. No real health data in the repo.
9. Clock rule: at each phase deadline, ship what passes tests, log what's missing in `docs/STATE.md`, move on. Never extend a phase past its slot without writing the reason in `docs/DECISIONS.md`.

## Skills
brainstorming (5 min max per phase) → writing-plans → subagent-driven-development → test-driven-development → systematic-debugging → verification-before-completion.
karpathy-guidelines on every diff. frontend-design + design-critique on every UI task; `docs/UI_BRIEF.md` is law.

## Process budget (12 h)
Full reviewer pass only for `router/`, `triage/guard.py`, `triage/ladder.py`, `constraints/`, `vitals/detector.py`.
Everything else: builder self-review + tests. Plans are one page per phase.

## Commands
api: `cd apps/api && uv run pytest -q` · `uv run alembic revision --autogenerate -m "<msg>" && uv run alembic upgrade head` · `uv run uvicorn nadi.main:app --reload` · `uv run python worker.py`
web: `cd apps/web && pnpm dev | pnpm build | pnpm test | pnpm e2e`
infra: `docker compose up -d` · evals: `cd apps/api && uv run python ../../evals/run.py`

## Models
Main session: opus. planner: opus. builder: sonnet. reviewer: opus. designer: sonnet. red-team: opus.
If plan limits bite, everything on sonnet.

## Compaction policy
Preserve: current phase + task, failing tests, open decisions, human to-do. Re-read `docs/STATE.md` after compaction (SessionStart hook prints it).

## Never
`push --force` · `rm -rf` outside build dirs · edit or print `.env` · skip a failing test · add a "skip safety" flag · purple/violet/navy hues · gradients on product screens · any paid service.
