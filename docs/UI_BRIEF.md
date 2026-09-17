# UI_BRIEF.md — DAARI. Direction: "Editorial instrument."

Paper, ink, one signal colour. A well-set journal that learned motion from Awwwards work, with data panels that read like instruments.
References are for **feel only** — never layout, never assets: wonjyou.com (counter preloader, type scale, marquee, confident whitespace) and current Awwwards SOTD.

## Palette — OKLCH tokens, `apps/web/styles/tokens.css`
| Token | Value | Use |
|---|---|---|
| `--bone` | `oklch(0.965 0.006 85)` | background |
| `--ink` | `oklch(0.18 0.01 60)` | text |
| `--graphite` | `oklch(0.42 0.01 60)` | secondary text, hairlines |
| `--signal` | `oklch(0.62 0.2 30)` | coral-red — the single accent; scam ≥ 0.5, the active path on the graph |
| `--sage` | `oklch(0.68 0.08 150)` | qualifies, held skills, "new since your last visit" |
| `--amber` | `oklch(0.78 0.15 80)` | scam 0.3–0.5 "check this", missing-skill chips, `Unknown` eligibility |

Dark mode flips bone/ink. **A unit test asserts no hue in 250–320 and no `gradient` on product screens.**
Banned: glassmorphism, glow, neon, purple/violet/navy. Shadows ≤ 1 px hairline + 4 px blur at 8%.
No hex literals in components — tokens only.

## Type
Display serif (Instrument Serif) 64–140 px headlines · grotesk (Geist) for UI · mono (Geist Mono) for **every number, unit, skill id and timestamp**.
Telugu and Hindi: **Noto Serif Telugu** for display, **Noto Sans Telugu** / **Noto Sans Devanagari** for UI. A Telugu string must never fall back to a Latin-only face — check the rendered glyphs, not the CSS.
Scale 1.25. Tabular numerals throughout.

## Motion — `motion` only
Springs (stiffness 260, damping 28). 120–240 ms micro-interactions. Number counters on stats.
The roadmap diff animates once: removed steps fade, added steps slide in, reordered steps travel. Then it settles.
`prefers-reduced-motion` respected — the diff becomes an instant state change with a static +/− list.
**The `d3-force` graph on `/path` owns the frame budget.** It pauses while audio streams; nothing else animates during either.

## Screens
- `/` — counter preloader → hero "One path engine. Two worlds." → live lead marquee → eight-engine spread → evidence numbers → Open demo. **30-minute designer cap** (§13 cut line 7: static hero + counter).
- `/onboard` — persona picker (Ravi / Priya / blank); goal, district, language, constraints. Rural path is a spoken self-description with confirm/deny chips.
- `/assess` — one question at a time. The ability line with its error band **tightening on screen** after each answer. "6 questions, done."
- `/path` — `d3-force` graph: node size = this week's demand, current path in `--signal`, held nodes filled, missing outlined. Right rail = steps with `why`, hours, free-course link, "I learned this". **Market shock** control. Diff panel showing `cause: learner | market`.
- `/leads` — cards: match % with a component breakdown popover (coverage / gap / fit / demand), missing-skill chips in amber, scam badge with its reasons, `source` + `fetched_at` in mono, Refresh, "N new".
- `/schemes` — why-you-qualify as a rule list in sage, documents checklist, apply steps, and the inline "we need one thing" question with a mic button.
- `/voice` — rural mode. Three big Telugu buttons. Push-to-talk ring. Live interim text while speaking. Streamed reply. Latency HUD (5 hops, p50/p95). Agent trace drawer.
- `/interview` — question, talk, transcript with the quoted spans highlighted, feedback list, metrics strip (text + prosody bands), follow-up card, attempt trend.
- `/evidence` — shared-engine counters + import-graph box, roadmap invariants, scheme precision@5, scam confusion matrix, match ablation bars (graph on vs off), voice p50/p95 per hop, feedback specificity, lead freshness, provider/tool mix, CI sha.

Agent trace is one shared component, used on `/voice`, `/leads` and `/schemes`.

## Non-negotiable content rules
- Every lead and scheme card renders `source` and `fetched_at`. A card without both is a bug, not a style choice.
- Every score shown is decomposable — the popover exists because the engine returns components.
- A scam badge always states its reasons. `Unknown` eligibility renders as a question, never as "qualifies".

## Grid & gates
12 columns, 24 px gutters, max 1440 px. Breakpoints 390 / 768 / 1024 / 1440. Every product screen works on a phone.
Gates: Lighthouse a11y ≥ 90 on product screens · keyboard-complete · contrast AA · design-critique before every handoff ·
reviewer rejects the default-shadcn look and anything identifiable as a reference site.
