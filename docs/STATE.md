# STATE.md — DAARI (Team ASURA) · SYNORA Track 1 · Problem 01

Spec: `DAARI_BUILD_PLAN.md`. Clock: §6. Cut lines: §13.
Updated 2026-09-17 by `/setup`.

## Now
**P1 Skeleton (0:00–0:40) — not started.**
First task: dispatch `planner` to write `docs/superpowers/plans/phase-1-skeleton.md` from §6's P1 row, acceptance tests first. Then scaffold `packages/core`, `apps/api`, `apps/web` and get `/health` green.

P1 gate (§6, verbatim): *`/health` green incl. tools, ASR, TTS, Adzuna, SerpAPI budget.*

## Phase status
| Phase | Slot | Status |
|---|---|---|
| P1 Skeleton | 0:00–0:40 | not started |
| P2 Engine (E1, E2, E5, E8 registry) | 0:40–2:30 | not started |
| P3 Live leads, demand, schemes (E3, E4) | 2:30–4:15 | not started |
| P4 Streaming voice + agent loop (E6, E8) | 4:15–5:45 | not started |
| P5 Interview (E7) | 5:45–7:15 | not started |
| P6 Evidence + polish | 7:15–8:15 | not started |
| P7 Rehearsal + audit | 8:15–9:15 | not started |
| Freeze + optional deploy | 9:15–10:00 | not started |

## Done at setup
- Operating layer rewritten for DAARI: `CLAUDE.md`, `.claude/rules/{core,api,web,data,safety}.md`, all five agents, all five slash commands.
- Infra config: `docker-compose.yml` (pgvector pg17 + redis 7, `daari` credentials), `.github/workflows/ci.yml` (core / api / web / evals jobs, ffmpeg installed in CI).
- `.env.example` rewritten for DAARI; `.gitignore` updated.
- Toolchain verified; **ffmpeg 9.0.1 installed** (early, per §15 finding 22).
- Versions pinned live from npm and PyPI → `docs/DECISIONS.md` D3.
- Hooks proven by execution: 18/18 sample payloads → `docs/DECISIONS.md` D6.
- MCP (context7, playwright) verified → D5.

## Blockers
**P1's health check cannot go green until the human to-do below is done.** Nothing else is blocked — the planner and the scaffolding can start immediately.

## Phone / human to-do
1. **Create `.env` and fill five keys.** Claude Code never creates or edits `.env`.
   ```
   cp .env.example .env
   ```
   Then fill, all free and card-less:
   - `GEMINI_API_KEY` — aistudio.google.com → "Get API key"
   - `GROQ_API_KEY` — console.groq.com → API keys (also powers ASR)
   - `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` — developer.adzuna.com → sign up
   - `SERPAPI_KEY` — serpapi.com → free plan, 100 searches/month, **no card**
   At least one of Gemini/Groq is required; Adzuna is required for demand weights. SerpAPI is §13 cut line 4 if it ever asks for a card.
2. **Install Microsoft Edge** — https://www.microsoft.com/edge. It is the demo browser: it ships native `te-IN` voices, which are the TTS fallback if `edge-tts` fails mid-pitch.
3. **Optional, on home Wi-Fi with ≥ 16 GB RAM:** `ollama pull llama3.1:8b` — the third link in the provider chain. Ollama is installed but has no models.
4. **Test the wired mic in the hall.** Push-to-talk, 5 cm from the mouth. §15 finding 15 calls hall noise the largest residual risk.
5. **Optional deploy keys** (only if you want the QR): Supabase, Upstash, HF token. Deploy is cut line 9 — the laptop is the primary demo.

## Next concrete action
`/go` — planner writes `docs/superpowers/plans/phase-1-skeleton.md`, then P1 scaffolding begins.
