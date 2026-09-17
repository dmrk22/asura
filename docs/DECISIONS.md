# DECISIONS.md — NADI (Team ASURA)

Append-only. Every deviation from `NADI_BUILD_PLAN.md`, every accepted risk, every cut line applied.

## Setup — 17 Sep 2026

### Versions verified at setup (never typed from memory)
Checked against the npm registry and PyPI on 17 Sep 2026.

**Web** — next 16.3.5 · react 19.3.0 · react-dom 19.3.0 · **typescript 5.9.3 (pinned, see below)** ·
tailwindcss 4.3.3 · @tailwindcss/postcss 4.3.3 · motion 13.4.0 · uplot 1.6.32 · zustand 5.0.15 ·
@tanstack/react-query 5.103.1 · react-hook-form 7.88.0 · zod 4.6.5 · @biomejs/biome 2.5.14 · @playwright/test 1.63.0

**API** — fastapi 0.141.1 · pydantic 2.13.5 · sqlalchemy 2.0.54 · alembic 1.20.0 · structlog 26.1.0 ·
fastembed 0.8.0 · river 0.26.1 · scikit-learn 1.9.1 · pytest 9.1.1 · hypothesis 6.168.0 · redis 8.1.0 ·
asyncpg 0.31.0 · pgvector 0.5.0 · uvicorn 0.53.0 · ruff 0.16.8 · pyright 1.1.414 · httpx 0.28.1 ·
pillow 12.3.0 · pyyaml 6.0.3 · joblib 1.6.0 · numpy 2.5.3 · google-genai 2.24.0 · groq 1.7.0

### D1 — TypeScript pinned to 5.9.3, not the latest 7.0.2
Latest published is 7.0.2 (the native port). Next 16 + Tailwind 4 + the `@types/*` ecosystem are not
uniformly proven on it, and a compiler surprise at hour 3 of a 12-hour build is unrecoverable.
5.9.3 is the current 5.x. **Accepted risk:** we are one major behind. Revisit never — not in this clock.

### D2 — Python 3.12 (not 3.14)
System Python is 3.14.7. `uv` has 3.12 available and the plan pins it; `river`, `fastembed` and
`scikit-learn` wheels are proven there. `uv` manages the interpreter, so the system version is irrelevant.

### D3 — Skills not vendored into `.claude/skills/`; already installed as plugins
Plan §5.4 says vendor karpathy-guidelines, frontend-design and design-critique when the marketplace lacks
them. It does not lack them — all three resolve on this machine:
- superpowers 6.3.0 — `~/.claude/plugins/cache/superpowers-marketplace/superpowers/6.3.0/`
- frontend-design — `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/`
- karpathy-guidelines — `~/.claude/plugins/marketplaces/karpathy-skills/skills/karpathy-guidelines/`
- design-critique-agent + design-audit — `~/.claude/skills/`
Vendoring would ship a second, staler copy. **Teammate laptops must install the same plugins** — this is
the one thing a lane laptop needs beyond `git clone`. Listed in STATE.md as a human to-do.

### D4 — No project-level `/setup` command
Plan §5.4 lists `/setup` among `.claude/commands/`. A project command of that name would shadow the global
`/setup` skill that bootstrapped this repo. The re-run behaviour it describes (compose up, baseline
migration, `/health`, STATE.md) is `/go`'s first task in P1. Five commands shipped: `/go /lane /demo /audit /ship`.

### D5 — `.mcp.json` written even though both servers are already plugin-provided
Context7 and Playwright respond here via plugins. `.mcp.json` is committed anyway so a lane laptop gets
them from `git clone` alone. Local duplication is harmless; a teammate without them is not.

### D6 — Deploy not initialised at setup
Vercel and Hugging Face CLIs are absent, and both need an interactive browser login that Claude Code
cannot perform. Deploy is optional (plan §10, cut line 8) and scheduled for hour 11:30. The laptop demo
is the primary. Install and login are human to-dos in STATE.md; `/ship` skips deploy if the values are blank.
