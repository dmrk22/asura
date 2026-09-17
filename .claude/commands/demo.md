---
description: Rehearse the demo with the network blocked. Run three times before the pitch.
---
1. `docker compose up -d`; wait for both healthchecks.
2. Start api (`uv run uvicorn nadi.main:app`), `uv run python worker.py`, and web (`pnpm dev`).
3. Seed persona Ravi: `cd apps/api && uv run python ../../scripts/seed.py --persona ravi`.
4. `uv run python ../../scripts/warm_cache.py` — executes every LLM call in `docs/DEMO.md` and stores the response by sha256 of its normalised input.
5. Replay `docs/DEMO.md` as a Playwright dry-run **with outbound network blocked** (route-abort every non-localhost request).
6. Report per demo beat: passed / failed, the wall-clock time, and the alert latency p50/p95 actually measured.

Any beat that needed the network is a failure, not a warning. Fix it by warming that call.
