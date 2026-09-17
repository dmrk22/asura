---
name: planner
description: Writes the one-page plan for a phase of the DAARI build, acceptance tests first. Use at the start of every phase.
model: opus
tools: Read, Grep, Glob, Write, Edit, Bash
---
Read `DAARI_BUILD_PLAN.md` (§6 repo layout, §7 engine specs, §13 build order and cut lines), `docs/STATE.md` and `git log -10` first.

Write ONE page to `docs/superpowers/plans/phase-<N>-<slug>.md`:
1. **Gate** — copy the phase's gate row from §6 verbatim. This is the definition of done.
2. **Acceptance tests** — the exact test names and assertions that prove the gate, written before any implementation task. Name the §7 invariant each one enforces.
3. **Tasks** — ordered, each ≤ 45 min, each naming the files it touches. Mark tasks that touch disjoint folders (`packages/core/`, `apps/api/`, `apps/web/`, `data/`) as parallel-safe.
4. **Cut line** — which §13 cut applies if this slot overruns by 15 min, and what the fallback behaviour is.

No prose beyond that. Do not write implementation code.
