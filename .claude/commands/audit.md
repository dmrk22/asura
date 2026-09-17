---
description: Adversarial audit. Blocks /ship until findings are fixed or accepted in writing.
---
1. Dispatch `red-team` against the running system.
2. Then dispatch `reviewer` over the full diff since the last `phase-*` tag.
3. Collect findings into `docs/DECISIONS.md` under `## Audit <date>`: finding | evidence | fixed or accepted | reason.
4. Re-run the evals and show the numbers: scheme precision@5, scam recall/precision, match ablation (graph on vs off), roadmap invariants, feedback must-mention recall, feedback adversarial violations, CAT termination, voice first-audio and total p95.

`/ship` is blocked while any finding is neither fixed nor accepted in writing.
