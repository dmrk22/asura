# DECISIONS.md — DAARI (Team ASURA)

Append-only. One line per decision: what, why, when. Reversals get their own entry.

## D1 · 2026-09-17 · Repo `asura` reused for DAARI, previous project removed
The working tree arrived with every file of the previous project (NADI, a health-triage build) deleted and `DAARI_BUILD_PLAN.md` added. `/setup` treated that as intentional and rebuilt the operating layer for DAARI rather than restoring NADI. The NADI tree remains recoverable at commit `a264545`.
Names: **repo and deploy target = `asura`** (the directory and the GitHub remote), **product = DAARI**, **Python packages = `daari_core` and `daari`**. Never name a deploy target after a previous project.

## D2 · 2026-09-17 · Toolchain verified at setup, not assumed
| Tool | Found |
|---|---|
| git | 2.55.0 |
| gh | 2.101.0, logged in as `dmrk22` |
| uv | 0.12.15 |
| pnpm | 12.3.4 |
| node | v22.23.2 |
| docker | 29.7.2, daemon up |
| ollama | 0.34.1, **no models pulled** |
| ffmpeg / ffprobe | 9.0.1 — **installed during this setup** |
| python3 (system) | 3.14.7 — the project pins 3.12 via `uv`, so this is not used |
| vercel CLI | not installed — deploy is optional (§13 cut line 9) |
| Microsoft Edge | not installed — **human to-do**, it is the demo browser for native te-IN voices |

ffmpeg was installed at setup rather than at P5, per §15 finding 22 (librosa/ffmpeg install stalls).

## D3 · 2026-09-17 · Versions pinned from the live registries, never from memory
Checked with `npm view <pkg> version` and the PyPI JSON API on 2026-09-17.

**Web**
| Package | Version |
|---|---|
| next | 16.3.5 |
| react / react-dom | 19.3.0 |
| typescript | 7.0.2 |
| tailwindcss / @tailwindcss/postcss | 4.3.3 |
| motion | 13.4.0 |
| zustand | 5.0.15 |
| @tanstack/react-query | 5.103.1 |
| react-hook-form | 7.88.0 |
| zod | 4.6.5 |
| d3-force | 3.0.0 |
| @playwright/test | 1.63.0 |
| @biomejs/biome | 2.5.14 |

**API / core**
| Package | Version |
|---|---|
| fastapi | 0.141.1 |
| pydantic | 2.13.5 |
| sqlalchemy | 2.0.54 |
| alembic | 1.20.0 |
| structlog | 26.1.0 |
| httpx | 0.28.1 |
| arq | 0.28.0 |
| networkx | 3.6.1 |
| numpy | 2.5.3 |
| fastembed | 0.8.0 |
| librosa | 1.0.0 |
| edge-tts | 7.2.8 |
| groq | 1.7.0 |
| google-genai | 2.24.0 |
| pytest | 9.1.1 |
| hypothesis | 6.168.0 |
| ruff | 0.16.8 |

**Risk flagged, not resolved:** TypeScript **7.0.2** is the native-port major, not the 5.x line. P1 must prove `pnpm typecheck` and `pnpm build` green on Next 16.3.5 before the web lane goes wide. If it fights, fall back to the latest 5.x and record the reversal here — that is a P1 decision, not a P5 surprise.

## D4 · 2026-09-17 · frontend-design and design-critique already installed — no vendored copy
`/setup` step 6 says to fetch `frontend-design` into `.claude/skills/` if missing. It is already installed from Anthropic's official plugin marketplace at
`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`,
invocable as `frontend-design:frontend-design`, alongside `anthropic-skills:design-critique-agent` and `design-audit`.
Vendoring a second copy into the repo would only create a version to drift. Not done deliberately. If the plugin is ever unavailable on the demo laptop, fetch it from `github.com/anthropics/skills` into `.claude/skills/frontend-design/` and record the source commit here.

## D5 · 2026-09-17 · MCP servers verified live, not just declared
`.mcp.json` declares `context7` (`@upstash/context7-mcp`, latest 4.1.1) and `playwright` (`@playwright/mcp`, latest 0.0.81). Both are also connected in-session as plugin servers. Verified `context7` with a live `resolve-library-id` call for Next.js — it returned `/vercel/next.js`. Playwright MCP verified by package resolution and the connected plugin server; not launched, to avoid opening a browser during setup.

## D6 · 2026-09-17 · Hooks proven by execution, not by reading
`.claude/hooks/pre-tool-guard.sh` was run against 18 sample payloads: 9 that must be blocked (force push in two spellings, `rm -rf` on a source dir and on the repo root, three ways of reading the env file, two ways of printing a secret) and 9 that must pass (`rm -rf` on build dirs, pytest, alembic, pnpm build, docker, ffmpeg, an ordinary push). 18/18 as specified. `ffmpeg` and `ffprobe` added to the permissions allow-list per §5.2.

## D7 · 2026-09-17 · `safety.md` repurposed rather than deleted
The previous project's `.claude/rules/safety.md` was health-triage-specific. Rewritten in place as DAARI's five guards (the LLM never decides · provenance or it doesn't ship · Scam Shield states its reasons · no praise without a quote · eligibility has three states). Keeping the filename keeps the guards where every agent already looks.

## D8 · 2026-09-17 · Not done at setup, deliberately
- **No `.env`.** It is human-owned; `/setup` never creates or edits it. The template `.env.example` was rewritten for DAARI (Adzuna, SerpAPI + budget, `DAARI_SEED`, TTS voices) — 5 keys need values before P1's health check goes green.
- **No cloud provisioning.** Deploy is §13 cut line 9 and the laptop is the primary demo. Supabase / Upstash / Vercel / HF are wired as optional keys only; `/ship` provisions them if the clock allows.
- **No notification target.** This project declares no Telegram/Slack integration, so `/setup` step 8 is a no-op. Add one to `.env.example` first if you want build pings.
- **No subagent routing check.** §5.1 asks `/setup` to dispatch a throwaway builder and grep its transcript for the model. Not run — dispatching a subagent for a setup task is a cost with no payoff until P1 has something to build. Do it as the first action of `/go`.
