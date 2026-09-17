---
description: Freeze main, tag v1-synora, optional ₹0 deploy if the clock allows.
---
1. Refuse if `/audit` has unresolved findings.
2. Full CI locally: ruff, biome, pyright, tsc, pytest, pnpm test, `evals/run.py`, Playwright smoke. All green or stop.
3. Commit `evals/report.json`. Tag `v1-synora`. Push.
4. **Optional deploy** — only if the four deploy values in `.env` are non-empty AND there are ≥ 20 minutes left:
   web → Vercel; api + worker → Hugging Face Space (Docker SDK, free CPU); DB → Supabase pooler; Redis → Upstash.
   `scripts/push_env.sh` sets the secrets. Never print a value.
5. Verify each deployed URL returns 200. Write the QR codes into `docs/DEMO.md`.
6. Print the final checklist: laptop demo green, three clean dry-runs, pitch ready, QR (or "laptop only").

The laptop demo is the primary. The QR is the bonus. Never trade the first for the second.
