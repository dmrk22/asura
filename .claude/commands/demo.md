---
description: Rehearse the demo with the network blocked. Run three times before the pitch.
---
1. `docker compose up -d`; wait for both healthchecks.
2. Start api (`cd apps/api && uv run uvicorn daari.main:app`), the refresh worker (`uv run arq daari.workers.WorkerSettings`), and web (`cd apps/web && pnpm dev`).
3. Seed both personas: `cd apps/api && uv run python ../../scripts/seed.py --persona ravi --persona priya`.
4. `uv run python ../../scripts/warm_cache.py` — for every beat in `docs/DEMO.md` it stores:
   - each LLM and tool-call response by sha256 of its normalised input,
   - the Groq Whisper transcript for each rehearsed Telugu clip,
   - the per-sentence `edge-tts` mp3 for each reply,
   - a snapshot of every lead and scheme fetch, with its original `fetched_at` preserved,
   - the placement-notice extraction and the demo companies' question corpus (§11 beat 4),
   - the grounding verifier's per-sentence verdicts, so the strike list is identical offline.
5. Replay `docs/DEMO.md` as a Playwright dry-run **with outbound network blocked** (route-abort every non-localhost request).
6. Report per demo beat: passed / failed, the wall-clock time, and the voice hop latencies actually measured (p50/p95 for ASR, LLM first token, engine, TTS first byte, total).

Any beat that needed the network is a failure, not a warning. Fix it by warming that call.
Beat 5 is the Constitution beat: the no-data reply and the declined estimate must reproduce offline, with the same struck sentences and reasons.
Snapshot leads still render `source` and `fetched_at` with a "stale since" note — never hide the stamp to make the demo look live.
