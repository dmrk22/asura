---
description: Adversarial audit. Blocks /ship until findings are fixed or accepted in writing.
---
1. Dispatch `red-team` against the running system.
2. Then dispatch `reviewer` over the full diff since the last `phase-*` tag.
3. Collect findings into `docs/DECISIONS.md` under `## Audit <date>`: finding | evidence | fixed or accepted | reason.
4. Re-run the safety evals and show the numbers: red-flag recall, adversarial violations, router held-out accuracy, latency p95.

`/ship` is blocked while any finding is neither fixed nor accepted in writing.
