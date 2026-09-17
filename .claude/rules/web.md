# web.md — apps/web

- Next.js App Router, TypeScript strict, Tailwind v4, `motion`, uPlot, Zustand, TanStack Query, react-hook-form + zod, shadcn primitives **restyled**.
- `docs/UI_BRIEF.md` is law. Tokens live in `styles/tokens.css` and nowhere else — no hex literals in components.
- A unit test asserts: no OKLCH hue in 250–320, no `gradient` on product screens. Do not weaken that test.
- Every number, unit and rule id renders in mono with tabular numerals.
- The vitals chart owns the frame budget. uPlot draws six 1 Hz lanes; nothing else animates while it streams.
- `prefers-reduced-motion` respected on every animation.
- Build against `mocks/` until the API lane lands. The mock shape and the Pydantic schema stay in sync — if they drift, the schema wins.
- Every product screen is usable at 390 px and keyboard-complete. Lighthouse a11y ≥ 90.
