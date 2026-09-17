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
