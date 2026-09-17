# web.md — apps/web

- Next.js App Router, TypeScript strict, Tailwind v4, `motion`, `d3-force`, Zustand, TanStack Query, react-hook-form + zod, shadcn primitives **restyled**. `MediaRecorder` + Web Speech API for voice.
- `docs/UI_BRIEF.md` is law. Tokens live in `styles/tokens.css` and nowhere else — no hex literals in components.
- A unit test asserts: no OKLCH hue in 250–320, no `gradient` on product screens. Do not weaken that test.
- Every number, unit, skill id and timestamp renders in mono with tabular numerals.
- **Provenance is visible.** Every lead and scheme card renders `source` and `fetched_at`. A card without both is a bug, not a style choice.
- **The force graph owns the frame budget.** `d3-force` on `/path` pauses while audio streams; nothing else animates during either.
- `prefers-reduced-motion` respected on every animation.
- Telugu and Hindi labels render in Noto Sans / Noto Serif Telugu. Never let a Telugu string fall back to a Latin-only face.
- Build against `mocks/` until the API lane lands. The mock shape and the Pydantic schema stay in sync — if they drift, the schema wins.
- Every product screen is usable at 390 px and keyboard-complete. Lighthouse a11y ≥ 90.

## v6 additions (plan §8, §12 of CLAUDE.md)
- **`next-intl` (4.14.5) is first-class.** `apps/web/messages/{en,te,hi}.json`; every screen and every string has all three. A test fails on a missing `te` key (`evals/i18n_check.py` is the CI gate). The header carries the language toggle (en/te/hi) and a mic button on **every** screen — Telugu is not the rural screen's feature, it is the product's.
- **Telugu never falls back to a Latin face**: Noto Sans Telugu / Noto Serif Telugu paired at the same optical size as the Latin face.
- **New screens**: `/prep` (notice → fields with spans → pack), `/questions` (dated, sourced company+role questions), and `/path` gains **two** controls — "Simulate skill update" and "Market shock" — each rendering explicit **Before | After** panes, a diff list with `cause`, and a cosine-shift chip.
- **Citation chips are structural.** A factual sentence renders with its citation chip or it is not shown. Struck sentences appear in the trace drawer with their reason, never silently.
- Agent trace drawer on every product screen. `/evidence` renders counters, the import-graph box, ablations, scheme precision + coverage, scam recall, voice p95 per hop, edges added today, last cosine shift, grounding F1, strike rate, no-data rate, the 13-row Constitution panel and the CI sha.
