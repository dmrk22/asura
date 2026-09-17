# DAARI by Team ASURA — SYNORA Track 1 (AI/ML) · Problem 01 · Master Build Plan v4 (post red + quality audit) · ₹0 stack

Written 17 Sep 2026. One file. Save it as `~/dev/asura/DAARI_BUILD_PLAN.md`, open Terminal in that folder, run `claude --model opus`, type `/setup` once, then `/model opusplan` and `/go` until the clock runs out. Claude Code creates the repo, code, tests, migrations, evals, deploy and demo script. You spend nothing: no card, no API credits.

Team: **ASURA**. Product: **DAARI** (దారి — "the way / the path"). Repo: `asura`.

v4 changes v3 in one direction: every engine was audited for "is this what a strong senior engineer would build, or a hackathon shortcut?" and upgraded where the answer was the second. §15 lists the 31 findings and what changed. Nothing in the operating layer (§5) or the UI direction (§8) changed.

---

## 0. The angle: one path engine, market-aware, two worlds

The statement asks for two personas on a shared matching engine. Every other team will ship a chatbot with an `if persona == "rural"` branch and a static roadmap. We ship one thing, and it moves:

**A Skill Graph that the live job market re-weights.** ~300 canonical skills with prerequisite edges, learning hours, Telugu labels and sources. A person is a set of nodes; a goal is a set of nodes; a roadmap is the cheapest path between them where "cheapest" is hours divided by live market demand — a skill that appears in 40% of this week's local listings gets pulled forward. The roadmap changes when the learner changes **and when the market changes**. A job is a set of required nodes plus a scam risk score. A scheme is a set of eligibility predicates evaluated deterministically, with the documents you need and the one question we still have to ask you. Voice, Telugu, the student UI and the rural UI are adapters. An LLM orchestrates by calling engine tools; it never decides a match.

Eight engines, one package:

| # | Engine | Rubric line it satisfies | What the judge sees |
|---|---|---|---|
| E1 | **Skill Graph + Explainable Matcher** — `packages/core`; level-aware coverage, graph-distance gap cost, embedding-based skill adjacency, transferability learned from live job co-occurrence | "Shared architectural engine … verified in code" | `/evidence`: one package imported by both persona routes, an AST test that forbids matching logic elsewhere, live call counters per persona, and an ablation (graph on/off) |
| E2 | **Market-Aware Adaptive Roadmap** — Dijkstra where edge weight = hours / (1 + demand); demand is recomputed from every live fetch; diff on learner change or market change | "Adaptive roadmap: before/after roadmap changes triggered by simulated skill updates"; "dynamic graph/vector updates in roadmaps" | Tap "I learned SQL" → re-route + diff. Judge presses **Market shock** ("+50 Power BI listings in Vijayawada") → the roadmap re-orders again, live, with the diff |
| E3 | **Live Leads + Scam Shield** — Adzuna India, Remotive, Google Jobs via SerpAPI, myscheme.gov.in, AP scheme pages; freshness stamps; "new since your last visit"; scam-signal scoring with reasons | "Live data sources … no hardcoded lists" | Every card: source, fetched-at, Refresh; scam-flagged listings show why ("asks for registration fee", "WhatsApp-only contact") |
| E4 | **Eligibility + Slot-Filling** — LLM-extracted predicate AST (temp 0, cached, snippet-justified), deterministic evaluation, document checklist, apply steps; missing fields become one spoken question | "Precision of RAG retrieval for regional schemes"; "vernacular government scheme awareness" | "Why you qualify" as a rule list; "we need one thing: your annual income" asked in Telugu, answered by voice, re-evaluated |
| E5 | **Adaptive Skill Assessment** — Rasch (1PL) computerized adaptive test per skill: next item by max information, stop at SE < 0.4 or 6 items; rural persona: skills extracted from a spoken self-description into taxonomy nodes with confidence, confirmed by tap | "Students: skill assessment" | 6 questions instead of 30; the ability estimate and its error bar tighten on screen; the roadmap uses the estimate, not a self-rating |
| E6 | **Streaming Voice + Telugu** — interim transcripts while speaking, sentence-chunked TTS that starts before the reply finishes, barge-in, language auto-detect (te / en / hi / Tenglish), 5-hop latency HUD | "Vernacular & voice I/O … first-class"; "voice latency" | Reply audio starts < 1 s after the transcript; HUD shows ASR / LLM-first-token / engine / TTS-first-byte / total |
| E7 | **Interview with Evidence + Prosody** — role- and JD-anchored questions, adaptive follow-up on the weakest STAR element, text metrics + prosody (WPM, pause ratio, pitch variability), quote-required feedback, praise guard | "Actionable interview feedback … avoiding generic praise"; "actionable depth of mock interview feedback" | Each feedback item highlights the candidate's own words; a metrics strip; a follow-up question generated from the gap; progress across attempts |
| E8 | **Agent Orchestrator** — tool-calling loop (Gemini / Groq native tools; JSON-mode fallback) over engine tools; visible agent trace with timings | "Build a unified, intelligent agent" | An **Agent trace** panel: which tools ran, with what, how long. The LLM's job is orchestration and words; every decision is a tool result |

Differentiators the judges have not seen today:
- **The market moves the roadmap.** Live listings feed demand weights into the graph; the roadmap is different on Monday than on Friday and says why. Judge control: Market shock.
- **Scam Shield.** Fake jobs are the rural youth's real enemy. Scoring with reasons, on every card.
- **CAT assessment.** Six questions, an estimate with an error bar, and a roadmap that consumes the estimate.
- **Slot-filling eligibility.** The system knows what it doesn't know and asks exactly one question, in Telugu, by voice.
- **Streaming voice.** Perceived latency under a second, measured, on screen.
- **Prosody.** Interview feedback that hears the pause, not just the transcript.
- **Agent trace + evidence page.** Everything the agent did, and everything we claim, visible.

---

## 1. Decision record

Problem 01 chosen at hour 2 after abandoning Problem 02. v3 was audited and found technically thin in five places (weighted-sum matcher, static roadmap weights, request-response voice, self-rated skills, text-only interview). v4 fixes those. The ₹0 stack, the Claude Code operating layer, the UI direction and the cache-everything demo discipline are unchanged. The clock rule applies from this line; the cut lines in §13 fall back to v3 behaviour per engine, never below it.

---

## 2. Tech stack — final, ₹0, verified at `/setup` (never from memory)

| Layer | Choice | Why |
|---|---|---|
| Monorepo | `packages/core` (pure Python engine) + `apps/api` (FastAPI, `uv`) + `apps/web` (Next.js, `pnpm`) + `data/` + `evals/` | "Shared" is a fact of the import graph |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 async, **Alembic**, `structlog`, `httpx`, `arq` | Alembic autogenerate: migrations are Claude Code's job |
| Graph + math | **NetworkX** (Dijkstra, topological order), **numpy** (Rasch estimation, PMI), skill embeddings via fastembed for adjacency | Real algorithms, all CPU, all local |
| DB | Postgres 17 + **pgvector**; local Docker `pgvector/pgvector:pg17`; prod Supabase free | Rows, vectors, graph tables, demand table, item bank in one DB |
| Cache / queue | **Redis 7** (local Docker; prod Upstash free) + `arq` | Fetch cache with TTL, refresh jobs, demand recompute, new-since-visit |
| **LLM (₹0)** | Chain: **Gemini** (AI Studio free; native function calling) → **Groq** (Llama 3.3 70B / Llama 4; native tools) → **Ollama** `llama3.1:8b` (if pulled) → cached. `llm/tools.py` normalises tool schemas across providers; JSON-mode pseudo-tool loop when a provider lacks tools | Free, no card; the agent loop survives failover |
| **ASR (₹0)** | **Groq `whisper-large-v3`** (final transcript, `language` auto or `te`) + browser Web Speech API for **interim** transcripts while speaking → `faster-whisper` small locally if pulled | Streaming feel from the browser, accuracy from Groq |
| **TTS (₹0)** | **`edge-tts`** (`te-IN-ShrutiNeural`, `hi-IN-SwaraNeural`, `en-IN-NeerjaNeural`) streamed per sentence → browser `speechSynthesis` fallback (run the demo in Edge; it ships te-IN voices) | Natural Indic voices, sentence streaming, no key |
| Prosody | **librosa** (+ `ffmpeg` webm→wav): speaking rate, pause ratio, pitch variability (pyin) | Real acoustic features in ~200 ms |
| Embeddings / rerank | `fastembed` `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` + `BAAI/bge-reranker-base` | Multilingual, CPU, zero network |
| Live data | **Adzuna** India (free key), **Remotive** (no key), **SerpAPI Google Jobs** (free 100/month, no card — used for local gig searches, cached, budgeted), **myscheme.gov.in** (search JSON; Playwright fallback), **AP scheme pages** (`data/sources.yaml`) | Three job sources, two scheme sources, every card stamped |
| Frontend | Next.js (App Router, latest), TypeScript strict, Tailwind v4, `motion`, **d3-force** (graph), Zustand, TanStack Query, react-hook-form + zod, shadcn primitives restyled, `MediaRecorder` + Web Speech API | As in the UI brief |
| Tests / evals | `pytest`, `hypothesis` (graph, Rasch, eligibility invariants), Playwright, `evals/run.py` → `report.json` | `/evidence` reads the report |
| CI/CD | GitHub Actions: lint, types, core tests, api tests (pgvector service), web tests, evals, Playwright; deploy on `main` if secrets exist | A red eval blocks deploy |
| Hosting (₹0, optional) | Vercel + Hugging Face Space (Docker) + Supabase + Upstash | Laptop is the demo; prod is the QR |
| Claude Code tooling | superpowers, karpathy-guidelines, Anthropic `frontend-design`, design-critique, Context7 MCP, Playwright MCP | §5 |

---

## 3. Your part — 30 minutes, in parallel with `/setup`

1. **Install**: Homebrew; `brew install git gh uv pnpm node@22 ffmpeg`; Docker Desktop; Claude Code native installer `curl -fsSL https://claude.ai/install.sh | bash`; `claude` once, log in (Max). Optional (≥ 16 GB, home Wi-Fi): `brew install ollama && ollama pull llama3.1:8b`. Install **Microsoft Edge** for the demo browser (native Telugu TTS voices as the fallback).
2. **Free keys** (no card): GitHub `gh auth login`; Google AI Studio → `GEMINI_API_KEY`; Groq → `GROQ_API_KEY`; Adzuna (developer.adzuna.com) → `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`; SerpAPI (serpapi.com, free plan, no card) → `SERPAPI_KEY`. Optional deploy: Supabase, Upstash, Vercel, HF token.
3. **Folder**: `mkdir -p ~/dev/asura && cd ~/dev/asura`; save this file as `DAARI_BUILD_PLAN.md`.
4. **Wired mic** (earphones with mic or a lapel mic). Push-to-talk, 5 cm from the mouth. Test in the hall.
5. **Telugu speaker** owns the data lane (§12). No Telugu speaker → strings reviewed by TTS read-back.
6. **Start**: `claude --model opus` → `/setup` → fill `.env` when it stops → on the green health check `/model opusplan` → `/go`. `/demo` at hour 8:15.

---

## 4. Repository layout

```
asura/
├── DAARI_BUILD_PLAN.md  CLAUDE.md  .mcp.json  docker-compose.yml  .github/workflows/ci.yml
├── .claude/  settings.json  rules/  agents/  commands/  skills/  hooks/
├── docs/  STATE.md  DECISIONS.md  UI_BRIEF.md  DEMO.md  superpowers/plans/
├── packages/core/daari_core/
│   ├── graph.py        # SkillGraph: nodes, prerequisite edges, demand weights, shortest_path, adjacency
│   ├── taxonomy.py     # ids, labels_en/te/hi, aliases, embeddings
│   ├── profile.py      # Profile: persona, held {skill: level±se}, goal, constraints
│   ├── match.py        # match(profile, candidates) -> ranked Match with component breakdown
│   ├── roadmap.py      # roadmap(profile, goal, demand) -> Path; diff(before, after)
│   ├── demand.py       # demand(listings) -> {skill: weight}; co-occurrence PMI -> transferability
│   ├── eligibility.py  # Predicate AST, evaluate(profile, rules) -> (qualifies, reasons, missing_fields)
│   ├── assess.py       # Rasch 1PL: item selection, ability update, stopping rule
│   ├── scam.py         # scam_score(listing) -> (score, reasons)  (rules layer; LLM layer lives in api)
│   ├── interview_metrics.py  # STAR, quantifiers, filler, JD coverage (text-only, pure)
│   └── telemetry.py    # per-persona call counters
├── packages/core/tests/
├── apps/api/daari/
│   ├── main.py config.py db.py deps.py
│   ├── llm/        chain.py tools.py cache.py gemini.py groq.py ollama.py
│   ├── agent/      loop.py registry.py trace.py     # tool-calling orchestrator over engine tools
│   ├── voice/      asr.py tts.py stream.py latency.py lang.py
│   ├── leads/      adzuna.py remotive.py serpapi_jobs.py myscheme.py ap_schemes.py normalize.py refresh.py scam_llm.py
│   ├── schemes/    extract_rules.py documents.py rag.py slots.py
│   ├── assess/     items.py session.py
│   ├── interview/  questions.py followup.py prosody.py feedback.py guard.py
│   ├── personas/   student.py rural.py           # thin adapters; both import daari_core
│   ├── models/ api/   # routers: profile, roadmap, leads, schemes, voice, assess, interview, agent, evidence
│   ├── alembic/ tests/ worker.py Dockerfile pyproject.toml
├── apps/web/app/   (landing) onboard assess path leads schemes voice interview evidence
├── apps/web/components/ lib/ styles/tokens.css mocks/ e2e/
├── data/
│   ├── taxonomy/skills.yaml roles.yaml
│   ├── items/items.yaml          # CAT item bank: skill, difficulty b, question, options, answer, source
│   ├── interview/questions.yaml  # role-tagged, STAR rubric anchors
│   ├── personas/*.json  sources.yaml
├── evals/  schemes_golden.jsonl  roadmap_cases.jsonl  match_pairs.jsonl  scam_golden.jsonl
│           feedback_golden.jsonl  feedback_adversarial.jsonl  voice_latency.py  run.py  report.json
└── scripts/  bootstrap.sh  seed.py  warm_cache.py  push_env.sh
```

---

## 5. How Claude Code runs this — the operating layer (unchanged from v3 except the module list)

### 5.1 `CLAUDE.md` (Claude Code writes this at `/setup`; under 100 lines)

```markdown
# DAARI (Team ASURA) — rules for Claude Code
Hackathon: SYNORA Track 1, Problem 01. Spec = DAARI_BUILD_PLAN.md. Read it, docs/STATE.md and `git log -10` at the start of every task.

## Non-negotiables
1. One engine. Both persona routes import daari_core. A test fails if apps/api/daari/personas/* contains matching, roadmap, eligibility, assessment or scam logic, or if either route bypasses daari_core. packages/core never imports FastAPI, SQLAlchemy, httpx or any LLM client.
2. No hardcoded leads. Every job or scheme shown comes from a fetcher with source_url and fetched_at; the UI renders both. Snapshots allowed only with the stamp visible.
3. The LLM never decides. Matching, roadmap, eligibility, ability estimate, scam score, metrics are deterministic engine calls. The LLM orchestrates (tool calls), extracts structure at temperature 0 (cached by sha256), and writes words. Every tool call is logged to the agent trace.
4. Feedback guard: every interview feedback item carries a verbatim quote from the transcript. Praise without a quote is rejected. Adversarial violations = 0.
5. Versions, model IDs, free-tier limits verified (Context7 / `npm view` / `uv pip index` / consoles) before use. Never from memory.
6. ₹0: no paid API, no card, no paid tier. SerpAPI's 100/month is a budget: rehearsal + demo only, cached.
7. The scripted demo path works with the network unplugged: cached LLM/tool responses, cached ASR for rehearsed clips, pre-rendered TTS, snapshot leads with stamps, local DB and Redis.
8. Synthetic personas only. Real live leads, fake people.
9. Clock rule: at each phase deadline, ship what passes tests, log what's missing in STATE.md, move on. Cut lines (§13) fall back per engine, never below v3 behaviour. Never extend a slot without a DECISIONS.md entry.

## Skills
brainstorming (5 min max per phase) → writing-plans → subagent-driven-development → test-driven-development → systematic-debugging → verification-before-completion. karpathy-guidelines on every diff. frontend-design + design-critique on every UI task; docs/UI_BRIEF.md is law.

## Process budget
Full reviewer pass only for packages/core/, agent/loop.py, schemes/extract_rules.py, interview/guard.py, voice/latency.py. Everything else: builder self-review + tests. One-page plans per phase. Up to three builders in parallel on disjoint folders.

## Commands
core: `cd packages/core && uv run pytest -q`
api: `cd apps/api && uv run pytest -q` · `uv run alembic revision --autogenerate -m "<msg>" && uv run alembic upgrade head` · `uv run uvicorn daari.main:app --reload` · `uv run arq daari.leads.refresh.WorkerSettings`
web: `cd apps/web && pnpm dev | pnpm build | pnpm test | pnpm e2e`
infra: `docker compose up -d` · evals: `uv run python evals/run.py`

## Models (aliases on the Anthropic API: opus = Opus 5, sonnet = Sonnet 5, haiku = Haiku 4.5; never pin version strings here)
- /setup runs in a session started with `claude --model opus`. After the green health check the human switches to `/model opusplan`.
- Subagent frontmatter: planner opus · builder sonnet · reviewer opus · designer sonnet · red-team opus. Effort default (high) everywhere.
- Routing check: /setup dispatches one throwaway builder and greps its transcript under ~/.claude/projects/<proj>/<session>/subagents/ for "model". If not sonnet: unset CLAUDE_CODE_SUBAGENT_MODEL (never set it to inherit), restart, re-check; if it still fails, note in DECISIONS.md and continue on opusplan.
- If plan limits bite: `/model sonnet`, all agents sonnet.

## Compaction policy
Preserve: current phase + task, failing tests, open decisions, human to-do. Re-read STATE.md after compaction.

## Never
push --force · rm -rf outside build dirs · edit or print .env · skip a failing test · hardcode a lead · put engine logic outside packages/core · let the LLM return a match/score/eligibility directly · purple/violet/navy hues · gradients on product screens · any paid service.
```

### 5.2 `.claude/settings.json` — identical to v3 (permissions allow-list + SessionStart / Stop / PreToolUse hooks; `ffmpeg` added to the allow-list). `/setup` validates syntax against https://code.claude.com/docs/en/hooks and /docs/en/settings.

### 5.3 Subagents — identical to v3: `planner` (opus), `builder` (sonnet, up to three in parallel), `reviewer` (opus; five safety-critical modules only), `designer` (sonnet), `red-team` (opus; now also tries: an LLM-returned score reaching the UI, a scam listing passing unflagged, a roadmap that lengthens after learning a skill, a CAT session that never stops, a tool call missing from the trace).

### 5.4 Slash commands — identical to v3. `/setup` health check now returns `{sha, db, redis, llm:[…], tools: gemini|groq, asr: groq, tts: edge, adzuna, serpapi_budget_left}`; `/demo` warms LLM + tool responses, ASR for the rehearsed clips, TTS renders per sentence, and all lead fetches, then replays with the network blocked.

---

## 6. The 10-hour clock

Three builders and one designer run in parallel from 0:40 (core / api / web), merged every 90 minutes. Every slot ends with tests green, evals green, STATE.md updated, tag `phase-N`. Slot overrun > 15 min → §13.

| Slot | Phase | Core / API lanes | Web lane | Gate |
|---|---|---|---|---|
| 0:00–0:40 | **P1 Skeleton** | compose, `packages/core` stub, FastAPI `/health`, Alembic, `llm/chain.py` + `tools.py` (tool schema normalisation + JSON-mode fallback), CI, subagent routing check | Next.js, tokens, shell, mocks, persona switch, "DAARI · online" | `/health` green incl. tools, ASR, TTS, Adzuna, SerpAPI budget |
| 0:40–2:30 | **P2 Engine** (E1, E2, E5 core, E8 registry) | `skills.yaml` (300, Telugu + Hindi labels, sources), `roles.yaml` (40), `items.yaml` (≥ 8 items × 3 difficulties for the 12 skills in the two demo roles + 60 generic); `graph.py`, `taxonomy.py` (label embeddings, adjacency ≥ 0.75 cosine), `profile.py`, `match.py` (§7.2), `roadmap.py` + `diff()` with demand weights (demand stub = 1.0 until P3), `assess.py` (Rasch, §7.5), `telemetry.py`; `agent/registry.py` exposes engine functions as tools with Pydantic schemas; hypothesis tests (§7 invariants) + AST shared-engine test | `/onboard` (persona; rural = spoken self-description mock), `/assess` (CAT UI: one question at a time, ability + error bar tightening), `/path` (d3-force graph, current path in signal, node size = demand, "I learned this" toggles, diff panel) | Learning a required skill never lengthens the path; CAT stops at SE < 0.4 or 6 items; AST test passes; tool registry lists 9 tools |
| 2:30–4:15 | **P3 Live leads, demand, schemes** (E3, E4) | fetchers (Adzuna, Remotive, SerpAPI Google Jobs budgeted, myscheme, AP pages), `normalize.py` (skills via alias table + LLM temp 0), `refresh.py` (arq, 15 min, on-demand, "new since last visit" per profile), `demand.py` (skill frequency per district + PMI co-occurrence → transferability edges) feeding `roadmap` weights; `scam.py` rules (§7.3) + `scam_llm.py` second opinion cached; `extract_rules.py` (predicates + documents + apply steps, snippet-justified), `eligibility.py`, `slots.py` (missing field → one question), `rag.py` hybrid + eligibility filter; evals: scheme precision@5 ≥ 0.8, scam recall ≥ 0.9 on 30 golden, match ablation on 40 pairs | `/leads` (cards: match % with breakdown popover, missing-skill chips, scam badge with reasons, source + fetched-at + Refresh, "3 new"), `/schemes` (why-you-qualify rules, documents checklist, apply steps, "we need one thing" prompt), **Market shock** control on `/path` (right rail: pick a skill, +N listings → roadmap re-routes + diff) | Ravi: schemes he qualifies for + one "needs: income" question; a fee-asking listing shows the scam badge; Market shock re-orders Priya's roadmap with a diff |
| 4:15–5:45 | **P4 Streaming voice + agent loop** (E6, E8) | `agent/loop.py` (§7.8): tool-calling loop, max 6 tool calls, trace with timings; `voice/stream.py`: WebSocket session — browser interim transcripts, final transcript via Groq Whisper, LLM streaming tokens → sentence splitter → `edge-tts` per sentence → audio chunks back; barge-in cancels TTS + LLM; `lang.py` detect (te / en / hi / Tenglish) from ASR + script; `latency.py` 5 hops; `evals/voice_latency.py` on 10 rehearsed clips: first audio p95 < 1.5 s, total p95 < 4 s | `/voice` rural mode (three big Telugu buttons, push-to-talk ring, live interim text, streamed reply, **Agent trace** drawer, latency HUD), agent trace component reused on `/leads` and `/schemes` | "నాకు గుంటూరు దగ్గర పని కావాలి" → audio starts < 1.5 s; trace shows `search_jobs`, `scam_score`, `match`, `find_schemes`, `evaluate_eligibility` with ms each |
| 5:45–7:15 | **P5 Interview** (E7) | `questions.py` (bank + one JD-anchored), `followup.py` (weakest STAR element → one follow-up), `prosody.py` (librosa: WPM, pause ratio, pitch std; ffmpeg webm→wav), `interview_metrics.py` in core, `feedback.py` (schema §7.7), `guard.py`; progress across attempts; evals: must-mention recall ≥ 0.8, adversarial = 0 | `/interview`: question, talk (reuses P4 streaming), transcript with highlighted quotes, feedback list, metrics strip (text + prosody), follow-up card, attempt history | Priya answers → 4 quoted items + prosody strip + one follow-up; generic praise rejected in the test |
| 7:15–8:15 | **P6 Evidence + polish** | `/api/evidence`: report.json + live counters + fetch ages + provider/tool mix + ablation | `/evidence` big numbers, import-graph box, confusion of scam golden, ablation bars; landing (counter + hero + live lead marquee, 30 min cap); 390 px pass | Playwright e2e covers the demo; Lighthouse a11y ≥ 90 |
| 8:15–9:15 | **P7 Rehearsal + audit** | `/audit` → fix → `/demo` ×3 network-blocked; record the four demo clips; cache everything | same | three clean runs; `docs/DEMO.md`; `docs/pitch.md` (8 slides) |
| 9:15–10:00 | **Freeze + optional deploy** | `/ship` | same | `main` frozen; laptop primary |

---

## 7. Engine specifications (what mentors will interrogate)

### 7.1 Skill Graph (`daari_core.graph`, `taxonomy`)
Nodes `{id, label_en, label_te, label_hi, aliases[], level 1–5, hours, source, embedding}`; ~300 across tech, trades/livelihoods and cross-cutting skills. Prerequisite edges weighted by hours. **Adjacency** edges (no prerequisite, similar skill) from label-embedding cosine ≥ 0.75 (Tableau ↔ Power BI) with weight = 0.3 · hours. **Transferability** edges learned at runtime from live listings: PMI(skill_a, skill_b) over fetched job descriptions ≥ 1.0 → edge with weight = hours · (1 − min(PMI/3, 0.5)). Sources per node: NSQF descriptors, NCO-2015, ESCO labels, Skill India / NPTEL free-course links.

### 7.2 Matcher (`daari_core.match`)
`match(profile, candidates) -> [Match{score, components{coverage, gap_cost, constraint_fit, demand_bonus}, missing[], surplus[], reasons[]}]`. Coverage is level-aware (held level ≥ required level counts 1.0, one level short counts 0.5, uses the CAT estimate's lower bound when available). Gap cost = shortest-path hours from the held frontier to each missing skill (prerequisite + adjacency + transferability edges), normalised by the role's total hours. Constraint fit: location radius, language, schedule, minimum pay. Demand bonus: the candidate's skills' current district demand. Score = 0.5 · coverage − 0.25 · gap + 0.15 · fit + 0.10 · demand; every component returned and shown in a popover. Ablation on `/evidence`: precision@5 on 40 golden profile–job pairs with graph edges on vs. off.

### 7.3 Roadmap, demand, diff (`daari_core.roadmap`, `demand`)
`demand(listings_by_district) -> {skill: w}` where w = 1 + log(1 + share_of_listings_mentioning_skill · 10); recomputed on every refresh and on Market shock. `roadmap(profile, goal, demand) -> Path{steps[{skill, hours, why[]}], hours, weeks_at(hpw)}`: Dijkstra over prerequisite + adjacency + transferability edges with weight = hours / demand[target-side skill]; merged per missing skill and topologically ordered; each step carries `why` ("prerequisite for Power BI", "in 38% of Vijayawada listings this week"). `diff(before, after) -> {removed[], added[], reordered[], hours_delta, cause: learner|market}`. Invariants: learning a required skill never lengthens the path; a demand increase for a skill never moves it later; empty diff when nothing changed; both persona adapters produce identical output for identical inputs.

### 7.4 Leads + Scam Shield (`apps/api/daari/leads`, `daari_core.scam`)
`Lead{source, source_url, fetched_at, title, org, location, pay, description, required_skills[], scam{score, reasons[]}, new_since_visit}`. Sources: Adzuna India (district radius 40 → 100 km fallback), Remotive, SerpAPI Google Jobs (local gig queries: delivery, retail, driver, technician; ≤ 30 calls at rehearsal, cached), myscheme.gov.in, AP pages. Scam rules (score 0–1): asks for fee/registration/training payment (+0.5), WhatsApp/Telegram-only contact (+0.2), pay > 3× district median for the role (+0.2), no verifiable org (+0.1), "earn from home, no skills" phrasing (+0.2), free-mail employer domain (+0.1). LLM second opinion (temp 0, cached) adds ≤ 0.2 with a quoted reason. ≥ 0.5 → red badge with reasons; 0.3–0.5 → amber. Golden set of 30 (15 scam patterns, 15 clean): recall ≥ 0.9, precision ≥ 0.8. A repo-scan test forbids lead literals outside fixtures.

### 7.5 Adaptive assessment (`daari_core.assess`)
Rasch 1PL: item difficulty b in {−1, 0, +1} × ≥ 8 items per skill for the 12 demo-role skills, 60 generic; P(correct) = σ(θ − b). Session per skill: start θ = 0, choose the unanswered item maximising information I(θ) = P(1−P), update θ by Newton–Raphson on the log-likelihood after each answer, SE = 1/√ΣI; stop when SE < 0.4 or 6 items. Map θ to level 1–5 with the SE as an error bar; `profile.held[skill] = (level, se)`. Rural persona: a spoken self-description → LLM extraction into taxonomy ids with confidence (temp 0, cached) → confirm/deny chips; confirmed skills get level 2 with se 0.8; a CAT session is offered per skill. Property tests: SE decreases monotonically; a respondent who answers all correctly ends with θ ≥ +1; stopping rule always terminates.

### 7.6 Eligibility, documents, slot-filling (`daari_core.eligibility`, `schemes/*`)
`extract_rules.py`: scheme text → `{rules: {all:[…], any:[…]}, documents:[…], apply_steps:[…]}`, each predicate stored with the justifying snippet; fields: age, state, district, gender, category, annual_income, occupation, education, land_holding, disability, bpl. `evaluate(profile, rules) -> (qualifies: True|False|Unknown, reasons[], missing_fields[])`; Unknown never renders as "qualifies". `slots.py`: when a top-ranked scheme is Unknown on exactly one field, the agent asks one question in the user's language; the answer updates the profile and re-evaluates. `rag.py`: multilingual embeddings + tsvector, RRF top-20, rerank top-8, eligibility filter, return with `why_you_qualify`, `documents`, `apply_steps`, `source_url`. Precision@5 on 40 golden queries (half Telugu) ≥ 0.8.

### 7.7 Interview (`interview/*`, `daari_core.interview_metrics`)
Five questions: four from the bank filtered by the goal's skills, one anchored to a live JD. Answer by streaming voice. Text metrics (core, pure): STAR coverage by cue phrases, quantifiers, filler rate, JD keyword coverage, duration. Prosody (`prosody.py`, librosa): words per minute, pause ratio (silence > 500 ms / total), pitch std (pyin), long-pause count; reported as bands (e.g., "pace 92 wpm — slow band"). Feedback schema `[{point, quote (verbatim substring), fix, severity, source: text|prosody}]`, 3–6 items; `guard.py` rejects items without a valid quote or with praise phrases lacking one; one rewrite at temp 0, then metrics-only template. `followup.py`: the weakest STAR element → one follow-up question ("You described the task; what did you personally do?"). Attempt history shows the metrics trend. Evals: must-mention recall ≥ 0.8; adversarial violations = 0; specificity score on `/evidence`.

### 7.8 Agent orchestrator (`agent/*`)
Tools (all thin wrappers over `daari_core` or fetchers, Pydantic-typed): `get_profile`, `update_skill`, `assess_next_item`, `get_roadmap`, `search_jobs`, `scam_score`, `match_leads`, `find_schemes`, `evaluate_eligibility`, `start_interview`, `interview_feedback`. Loop: system prompt with persona + language + profile summary → LLM with tools → execute → append → repeat, ≤ 6 calls; every call logged `{tool, args, ms, provider}` to the trace and to `/evidence` counters. The LLM's final message is words only; any number, score or eligibility in it must have come from a tool result (a test compares the reply's numbers against the trace). Provider chain with tool-schema normalisation; JSON-mode fallback emulates tool calls when a provider lacks them.

### 7.9 Streaming voice (`voice/*`)
WebSocket `/ws/voice`: client sends interim transcripts (Web Speech, `te-IN`/`en-IN`) and, on release, the audio blob; server runs Groq Whisper for the final transcript, detects language, starts the agent loop with streaming tokens, splits sentences, renders each with `edge-tts` and streams audio chunks; the client plays chunks in order. Barge-in: pressing talk cancels the LLM stream and TTS. Five stamps: `t_release`, `t_asr_final`, `t_llm_first_token`, `t_engine_done`, `t_audio_first_chunk` (+ `t_audio_start` in the browser); HUD shows each segment, p50/p95 over the session. Fallbacks: browser ASR final → Groq; edge-tts → browser `speechSynthesis`. Cached: transcripts and per-sentence mp3 for the rehearsed clips.

### 7.10 LLM provider chain (`llm/*`)
`complete(task, messages, tools|schema, temperature=0, stream=False)`: Gemini → Groq → Ollama → cache; circuit breaker (3 failures or 429 → skip 60 s); cache key `sha256(task + model + normalised input)`; `warm_cache.py` pre-executes the demo. Logs provider, model, latency, cache hit, tool calls → `/evidence`.

---

## 8. UI brief — unchanged direction ("Editorial instrument": paper, ink, one signal colour, counter preloader, oversized display serif, marquee, hairlines, instrument-like data panels; reference wonjyou.com and Awwwards SOTD for feel only). Palette, type, motion and gates exactly as v3 (OKLCH tokens, hue ban 250–320 enforced by test, no gradients on product screens, Instrument Serif / Geist / Geist Mono + Noto Sans/Serif Telugu, springs 260/28, reduced-motion path, Lighthouse a11y ≥ 90, design-critique before every handoff).

Screens (v4): `/` landing; `/onboard`; `/assess` (one question at a time, ability line with error band tightening, "6 questions, done"); `/path` (d3-force; node size = demand, path in signal, held filled, missing outlined; right rail = steps with `why`, hours, free-course link, "I learned this"; **Market shock** control; diff panel with `cause`); `/leads` (match % + breakdown popover, missing chips amber, scam badge red/amber with reasons, source + fetched-at mono, Refresh, "N new"); `/schemes` (why-you-qualify in sage, documents checklist, apply steps, "we need one thing" inline question with mic); `/voice` (rural mode; three big Telugu buttons; push-to-talk ring; interim text; streamed reply; latency HUD; Agent trace drawer); `/interview` (question, talk, transcript with highlighted quotes, feedback, metrics strip incl. prosody bands, follow-up card, attempt trend); `/evidence` (shared-engine counters + import-graph box, roadmap invariants, scheme precision@5, scam recall/precision, match ablation bars, voice p50/p95 per hop, feedback specificity, lead freshness, provider/tool mix, CI sha). Agent trace is a shared component on `/voice`, `/leads`, `/schemes`.

---

## 9. Data (all free, all public)

9.1 Taxonomy (`skills.yaml`, `roles.yaml`): built in P2 from NSQF descriptors, NCO-2015, ESCO labels, Skill India / NPTEL course names; Telugu + Hindi labels via LLM at temp 0, reviewed by the data lane; every node has a `source`.
9.2 Item bank (`items.yaml`): ≥ 8 items × 3 difficulty bands for the 12 skills across the two demo roles (data analyst; delivery-and-retail livelihood), 60 generic (spoken English, basic numeracy, digital literacy). Each item has a source or a stated rationale; the data lane spot-checks 20.
9.3 Live sources: Adzuna India, Remotive, SerpAPI Google Jobs (budgeted), myscheme.gov.in, AP scheme pages in `sources.yaml` with licence/ToS notes; polite scraping (1 req/s, 15-min cache).
9.4 Personas: Ravi (22, Guntur district, 10th pass, OBC, family income unknown → the slot question, two-wheeler, Telugu only, wants income within 30 days); Priya (21, B.Tech CSE 3rd year, Vijayawada, Python + basic SQL, wants a data-analyst internship, English + Telugu); blank.
9.5 Evals: `schemes_golden.jsonl` (40), `roadmap_cases.jsonl` (20 incl. 8 market-shock cases), `match_pairs.jsonl` (40, for the ablation), `scam_golden.jsonl` (30), `feedback_golden.jsonl` (20) + `feedback_adversarial.jsonl` (30), `voice_latency.py` (10 rehearsed Telugu clips).

---

## 10. Run, CI, deploy — as v3. CI thresholds: scheme precision@5 ≥ 0.8; roadmap invariants pass; scam recall ≥ 0.9; match ablation shows graph-on ≥ graph-off; feedback adversarial = 0; must-mention recall ≥ 0.8; voice first-audio p95 < 1.5 s and total p95 < 4 s on cached clips; CAT termination test passes.

---

## 11. Demo script (6:45) and mentor Q&A

Laptop runs everything; scripted path works network-blocked; hotspot for live questions; wired mic; Edge browser.

1. (0:00) "Team ASURA. DAARI: one path engine that the job market re-weights, two worlds." Landing counter → Open demo.
2. (0:30) **Ravi, `/voice`.** Speak Telugu: "నాకు గుంటూరు దగ్గర పని కావాలి". Interim text appears while speaking; the Telugu reply starts under 1.5 s (HUD). Trace drawer: `search_jobs` (3 sources), `scam_score`, `match_leads`, `find_schemes`, `evaluate_eligibility` with ms. One listing carries a red scam badge — tap: "asks for ₹500 registration". One scheme says "we need one thing: your family's annual income" — Ravi answers by voice, it re-evaluates to "qualifies", with the documents checklist. Say: "Live sources, deterministic eligibility, a scam filter, Telugu in and out, every hop timed."
3. (2:15) **Priya, `/assess` → `/path`.** Six SQL questions; the ability line tightens; roadmap built from the estimate, node size = this week's demand. Tap "I learned SQL" → re-route + diff (cause: learner). Judge presses **Market shock: +50 Power BI listings** → re-route + diff (cause: market), "Power BI moved up 2 steps — 41% of listings this week". Say: "Same engine that planned Ravi's 30 days; both counters on the evidence page."
4. (4:00) **`/leads`.** Live internships, match % with the component popover, missing-skill chips; press Refresh; "2 new".
5. (4:45) **`/interview`.** Priya answers by voice → 4 quoted items + prosody strip (pace, pause ratio) + a follow-up on the missing Result. Say: "No praise without a quote — the guard rejects it; adversarial test at zero."
6. (5:45) **`/evidence`.** Shared-engine counters, import-graph box, ablation bars (graph on vs off), scheme precision, scam recall, voice p95 per hop, feedback specificity, freshness, CI sha.
7. (6:30) Close: one graph, two worlds, ₹0. Stop at 6:45.

Prepared answers (in `docs/DEMO.md`): why not Llama self-hosted / Pinecone / LinkedIn / self-hosted Whisper / IndicTrans2 / Twilio (as v3); *Is the engine shared?* separate package + AST test + live counters; *Is the roadmap really adaptive?* Dijkstra with demand-weighted edges; diff computed, not scripted; 20 property tests incl. market shocks; *Why a Rasch model?* six informative questions beat thirty; the SE is honest and feeds the matcher's lower bound; *Scam detection false positives?* precision on the golden set is on screen; amber means "check", red means "reasons listed"; *Is the LLM deciding anything?* no — a test compares every number in the reply with the tool trace; *Voice latency?* five hops, p50/p95 on screen, the free ASR is the bottleneck and the number is honest; *What's next?* NCS + Skill India APIs, WhatsApp voice notes, counsellor dashboard, more languages.

---

## 12. Teammates — as v3: lanes `core | api | web | data`, worktrees, merge windows at 2:30, 4:15, 5:45, 7:15; the data lane owns taxonomy review, Telugu/Hindi labels, item-bank spot-checks, golden sets, the four demo clips, pitch slides.

---

## 13. Cut lines (per engine, fall back to v3 behaviour, never below; apply on a 15-minute overrun)

1. E6 streaming → whole-reply TTS (still measured). 2. E7 prosody → text metrics only; follow-up → skipped. 3. E5 CAT → fixed 6-question quiz per skill (still an estimate, no SE). 4. E3 SerpAPI → skipped (Adzuna + Remotive remain); scam LLM layer → rules only. 5. E4 slot-filling → "needs: X" shown, not asked. 6. E1 transferability edges → adjacency only. 7. Landing → static hero + counter. 8. Persona "blank" → skipped. 9. Deploy → skipped.
Never cut: `packages/core` + tests, AST shared-engine test, demand-weighted roadmap + Market shock, freshness stamps, eligibility predicates, scam rules, feedback guard, agent trace, latency HUD, evidence page, cache warm-up.

---

## 14. Quality audit — what "advanced" means here, and where v3 was not

| Engine | v3 (basic) | v4 (advanced) | Why a mentor will notice |
|---|---|---|---|
| Matcher | hand-weighted keyword coverage | level-aware coverage using CAT lower bounds, graph gap cost over three edge types, transferability learned from live co-occurrence, component breakdown, ablation | "Show me it's better than keyword search" has a number |
| Roadmap | static hours, learner-only re-route | demand-weighted Dijkstra, market-driven re-route, `why` per step, Market shock control | The rubric's "dynamic graph updates" is literal |
| Skills | self-rating | Rasch CAT with SE, spoken-extraction for rural | "Skill assessment" is a model, not a form |
| Leads | fetch + stamp | + scam scoring with reasons, new-since-visit, three job sources | Impact criterion; nobody else will have it |
| Schemes | predicates | + documents, apply steps, Unknown state, one-question slot-filling by voice | Precision plus completion |
| Voice | request → response | interim transcripts, sentence-streamed TTS, barge-in, language detect, five hops | Perceived latency < 1.5 s, measured |
| Interview | text metrics + quotes | + prosody, adaptive follow-up, attempt trend | "Actionable depth" heard, not just read |
| Orchestration | routes to engine | tool-calling agent with a visible trace and a numbers-must-come-from-tools test | "Intelligent agent" that is auditable |

---

## 15. Red-team audit — v4 (31 findings)

**Judge simulation.** (1) "Shared engine?" → package + AST test + counters + ablation. Fixed. (2) "Adaptive?" → learner and market diffs, property tests, Market shock control. Fixed. (3) "Hardcoded?" → stamps, Refresh, repo-scan test. Fixed. (4) "Speak now" → push-to-talk, wired mic, interim text, editable transcript, cached clips. Fixed. (5) "Generic feedback" → quote-required schema, guard, adversarial 0, prosody. Fixed. (6) "Is the LLM making things up?" → numbers-from-tools test, trace on screen. Fixed. (7) "Why should a rural user trust these jobs?" → Scam Shield with reasons and a golden set. Fixed.

**Technical honesty.** (8) Rasch with LLM-written items has no empirical calibration → difficulty bands are stated assumptions; the pitch says "seed item bank, three difficulty bands, calibrated later from responses"; the SE is still mathematically honest for the model. Accepted. (9) PMI over a few hundred listings is noisy → transferability edges only when count ≥ 5 and PMI ≥ 1.0, weight-limited; cut line 6. Mitigated. (10) Demand from Adzuna over-represents IT → per-district share, SerpAPI local gig queries, cap the demand multiplier at 2×. Mitigated. (11) Prosody on a 15-second clip is thin → reported as bands, never as a score; text metrics carry the weight. Accepted. (12) Whisper Telugu accuracy → domain prompt, short utterances, editable transcript, honest HUD. Accepted. (13) LLM-extracted predicates → snippet per predicate, Unknown state, golden precision. Mitigated. (14) Scam rules can flag legitimate small employers → amber band for 0.3–0.5, precision on screen, reasons always shown. Mitigated.

**Demo reliability.** (15) Hall noise → as (4); the pitch never depends on one live utterance. Mitigated; largest residual risk. (16) Any source down → snapshot + "stale since". Fixed. (17) Groq 429 (LLM or ASR) → chain and browser ASR; cached clips. Fixed. (18) edge-tts breaks → pre-rendered sentences; Edge's native te-IN voices. Fixed. (19) Gemini tool calling differs from Groq's → `tools.py` normalisation + JSON-mode fallback tested in P1. Fixed. (20) WebSocket + MediaRecorder quirks across browsers → demo in Edge, tested in Chrome; Playwright e2e covers the voice path with a recorded blob. Fixed. (21) SerpAPI budget exhausted by rehearsals → ≤ 30 calls, cached, counter in `/health`. Fixed. (22) librosa/ffmpeg install stalls → installed in P1 skeleton, not P5; cut line 2. Fixed.

**Clock.** (23) v4 is heavier than v3 in 10 hours → three parallel builders, engine before visuals, per-engine cut lines that fall back to v3 (never below), 15-minute trigger. Accepted: the plan is deliberately over-scoped with a controlled descent. (24) Streaming voice is the riskiest new engineering → isolated in P4 with whole-reply TTS as the first commit and streaming as the second; cut line 1. Fixed. (25) CAT UI and item bank could stall P2 → items only for the 12 demo-role skills + 60 generic; the graph and roadmap commit first. Fixed. (26) Claude Max limits with three sonnet builders + opus reviewer → routing check at `/setup`, "all sonnet" fallback. Mitigated.

**Money.** (27) Every service free and card-less; SerpAPI free plan verified at `/setup`; if it needs a card, cut line 4 applies. Fixed.

**Team.** (28) No Telugu speaker → TTS read-back review. Mitigated. (29) Multiple laptops → lanes, windows, integrator. Fixed.

**Design.** (30) UI direction unchanged per instruction; new screens (`/assess`, Market shock, trace drawer, scam badge, prosody strip) specified within the same tokens; hue-ban test unchanged. Fixed. (31) Graph + streaming audio + motion could fight for the frame budget → d3-force pauses while audio streams; reduced-motion path. Fixed.

Verdict: pass. Thirty-one findings; twenty-four fixed, seven accepted with the reason stated. The plan is intentionally above what 10 hours comfortably holds; the descent is controlled by engine, not by panic.
