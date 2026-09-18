# builder-core scratch — 4 new pure modules

Scope: packages/core/ only. Did not touch apps/, data/, or existing daari_core modules.

## Added
- daari_core/scam.py — score(listing, *, pay_band=DEFAULT_PAY_BAND) -> ScamResult
  6 rules: upfront_fee(0.45), personal_contact_only(0.25), no_org(0.15),
  pay_out_of_band(0.2), unverifiable_url(0.15), urgency_no_interview(0.2).
  Clamped to 1.0, band thresholds 0.5/0.3.
- daari_core/eligibility.py — evaluate(ast, facts) -> Verdict, three-valued Kleene logic.
  Leaf missing field or None value -> unknown, field added to missing_fields.
  matched = only leaves whose own raw outcome was true (not post-`not`).
- daari_core/geo.py — haversine_km(a, b), mean radius 6371.0088km, validates lat/lon ranges.
- daari_core/assess.py — 1PL Rasch CAT: start/next_item/update/should_stop.
  Item fields matched to real data/items/items.yaml keys (id, skill_id, band,
  text, answer, source, rationale) — NOT the speculative prompt_en/te/hi/options
  shape in the task brief, per the task's own note to check the YAML first.
  `update` uses a single Fisher-scoring step with a fixed RIDGE=0.5 prior
  precision rather than replaying full history, because AssessState.answered
  only stores (item_id, correct) — no per-item band to replay. This makes SE
  non-increasing by construction (Fisher info >= 0 always).

## Verification
- `cd packages/core && uv run pytest -q` -> 125 passed, 1 skipped (was 63 passed, 1 skipped before)
- `cd packages/core && uv run ruff check .` -> All checks passed (after ruff --fix removed 2 unused imports in test files + Mapping->collections.abc)
- test_purity.py (AST import-forbid walk) still passes — no new module imports anything outside stdlib.

## Not done / deferred
- Did not wire scam/eligibility/geo/assess into apps/api or apps/web — out of scope (other builders own those folders).
- Did not load data/items/items.yaml from core (core stays I/O-free); only read it once via Bash to check key names.
