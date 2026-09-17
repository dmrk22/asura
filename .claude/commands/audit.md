---
description: Adversarial audit. Blocks /ship until findings are fixed or accepted in writing.
---
1. Dispatch `red-team` against the running system. v6 additions to attack: a company fact with no evidence, a date newer than the data, a number absent from the tool trace, a struck sentence rephrased instead of removed, a missing `te` string, a notice field invented rather than extracted.
2. Then dispatch `reviewer` over the full diff since the last `phase-*` tag.
3. Collect findings into `docs/DECISIONS.md` under `## Audit <date>`: finding | evidence | fixed or accepted | reason.
4. Re-run the evals and show the numbers: scheme precision@5, scam recall/precision, match ablation (graph on vs off), roadmap invariants, feedback must-mention recall, feedback adversarial violations, CAT termination, voice first-audio and total p95, vector ablation (on vs off), grounding F1, no-data adversarial violations, intel recall, notice field accuracy, verifier p95, `i18n_check` missing-`te` count, and the Constitution article table.

`/ship` is blocked while any finding is neither fixed nor accepted in writing.
