# STATE — DAARI

Spec: [DAARI_BUILD_PLAN.md](../DAARI_BUILD_PLAN.md), v6, §13. Updated 2026-09-25.

## Current phase

**P1: skeleton and Constitution scaffold.** The 2026-09-25 cleanup restored the tracked product tree to the verified P1 baseline (`6539b31`). The standalone demo backend/frontend and all P2–P5 implementation added for the time-constrained demo are absent from the current tree. Git history retains those commits for reference; future implementation must follow the phase gates in the master plan.

The current web UI is a locale-aware DAARI status page. The API exposes `/health`. `packages/core` contains only purity, shared-engine boundary, and telemetry scaffolding. The baseline migration enables pgvector. The Constitution's 13 articles are scaffolded, not yet implemented or claimed green.

## Verification on 2026-09-25

| Gate | Result |
|---|---|
| Core tests and Ruff | 5 passed, 1 skipped; Ruff clean |
| API tests and Ruff | 6 passed; Ruff clean |
| Web typecheck, lint, unit tests, build | All green; 3 unit tests, webpack production build |
| API Pyright | 0 errors |
| English and Telugu HTTP pages | Both rendered localized P1 status text from the production build |
| Live `/health`, Postgres, Redis, providers | Not rechecked: Docker CLI is unavailable in this environment |

The old P1 probe measurements in Git history are dated 2026-09-18; they are not evidence of current provider status. No P2 tool registry exists yet, so `/health` reports tool count 0.

## Phase status

| Phase | Status |
|---|---|
| P1 skeleton + Constitution scaffold | Restored; code checks green, live health gate pending |
| P2 engine, CAT, tool registry | Not started in the current tree |
| P3 live data, schemes, grounding | Not started |
| P4 streaming voice, agent, i18n flows | Not started |
| P5 interview intelligence and prep | Not started |
| P6 evidence and polish | Not started |
| P7 rehearsal and audit | Not started |

## Next action

Finish the live P1 `/health` gate in §5.4 on a machine with Docker, then implement P2 from §13 with acceptance tests first. Keep `/health` and Constitution status honest as capabilities are added.
