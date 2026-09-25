# DAARI web — P1

This is the Next.js shell from the [master build plan](../../DAARI_BUILD_PLAN.md). It provides the English, Telugu, and Hindi locale routes, language toggle, design tokens, and the P1 status page. Product screens arrive in later phases.

```bash
pnpm install --frozen-lockfile
pnpm dev
pnpm typecheck && pnpm lint && pnpm test && pnpm build
```

The font files in `fonts/` are committed and loaded locally, so a production build does not fetch fonts from Google.
