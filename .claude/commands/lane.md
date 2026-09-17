---
description: Second-laptop worktree. `/lane core|api|web|data` — edits scoped to that folder only.
---
Argument is one of `core`, `api`, `web`, `data`.

1. `git worktree add ../asura-lane-$ARG -b lane/$ARG`
2. Write `../asura-lane-$ARG/.claude/state/lane.md` naming the ONE folder this lane owns:
   - `core` → `packages/core/`
   - `api` → `apps/api/`
   - `web` → `apps/web/`
   - `data` → `data/`, `evals/`, `docs/pitch.md`
3. Refuse every edit outside that folder. Say which lane owns it instead.
4. Merge windows are 2:30, 4:15, 5:45 and 7:15 on the §6 clock — integrator on `main` only. Never merge from a lane.
