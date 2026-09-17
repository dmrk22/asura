---
description: Second-laptop worktree. `/lane api|web|data` — edits scoped to that folder only.
---
Argument is one of `api`, `web`, `data`.

1. `git worktree add ../asura-lane-$ARG -b lane/$ARG`
2. Write `../asura-lane-$ARG/.claude/state/lane.md` naming the ONE folder this lane owns:
   - `api` → `apps/api/` · `web` → `apps/web/` · `data` → `data/`, `evals/`, `docs/pitch.md`
3. Refuse every edit outside that folder. Say which lane owns it instead.
4. Merge windows are 3:00, 5:00, 7:00, 8:30, 10:00 — integrator on `main` only. Never merge from a lane.
