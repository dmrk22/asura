# UI_BRIEF.md — NADI. Direction: "Clinical editorial."

Paper, ink, one signal colour. A well-set medical journal that learned motion from Awwwards work.
References are for **feel only** — never layout, never assets: wonjyou.com (counter preloader, type scale, marquee, confident whitespace) and current Awwwards SOTD in health/data.

## Palette — OKLCH tokens, `apps/web/styles/tokens.css`
| Token | Value | Use |
|---|---|---|
| `--bone` | `oklch(0.965 0.006 85)` | background |
| `--ink` | `oklch(0.18 0.01 60)` | text |
| `--graphite` | `oklch(0.42 0.01 60)` | secondary text |
| `--signal` | `oklch(0.62 0.2 30)` | coral-red — alerts and the single accent |
| `--sage` | `oklch(0.68 0.08 150)` | OK states |
| `--amber` | `oklch(0.78 0.15 80)` | URGENT |

Dark mode flips bone/ink. **A unit test asserts no hue in 250–320 and no `gradient` on product screens.**
Banned: glassmorphism, glow, neon, purple/violet/navy. Shadows ≤ 1 px hairline + 4 px blur at 8%.

## Type
Display serif (Instrument Serif or Fraunces) 64–140 px headlines · grotesk (Geist or Inter Tight) for UI ·
mono (Geist Mono) for **every number, unit and rule id**. Scale 1.25. Tabular numerals throughout.

## Motion — `motion` only
Springs (stiffness 260, damping 28). 120–240 ms micro-interactions. Number counters on stats.
Alert cards flash `--signal` for one frame, then settle. `prefers-reduced-motion` respected.
**The vitals chart owns the frame budget — nothing animates while it streams.**

## Screens
- `/` — counter preloader → hero "Your body's whole day. One agent." → live vitals miniature from the local WS → capabilities marquee → five-engine spread → evidence numbers → Open demo. **30-minute designer cap.**
- `/onboard` — persona picker (Ravi / Priya / Arjun / blank); conditions, meds, allergies, goals, measures. Three steps.
- `/today` — chat centre; left rail profile + active constraints; right rail alerts + mode chip; urgency card above the composer; citations drawer; handoff sheet.
- `/vitals` — full-width uPlot six lanes, band overlays, alert markers; right panel timeline + Inject menu + latency HUD; time-scale slider.
- `/meals` — drop zone, dish rows with portion chips (−/+ roti, katori), macro range bars, trace panel, log.
- `/evidence` — big numbers (router accuracy, red-flag recall, adversarial violations, latency p95, tests passing, provider mix); confusion-matrix heatmap; CI run link; sha.

## Grid & gates
12 columns, 24 px gutters, max 1440 px. Breakpoints 390 / 768 / 1024 / 1440. Every product screen works on a phone.
Gates: Lighthouse a11y ≥ 90 on product screens · keyboard-complete · contrast AA · design-critique before every handoff ·
reviewer rejects the default-shadcn look and anything identifiable as a reference site.
