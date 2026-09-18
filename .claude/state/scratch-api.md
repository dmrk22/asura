# scratch-api builder log — live fetchers + skills_map + llm chain (P3 slice)

## Scope
apps/api/ only, plus new data/sources.yaml. Did not touch packages/core/ or apps/web/.

## Built
1. `data/sources.yaml` — remotive, adzuna, myscheme (public x-api-key moved here,
   not .env), nominatim, glassdoor (never fetched, entry records the exclusion).
2. `apps/api/daari/http.py` — shared client factory (browser UA, 10s timeout,
   follow_redirects), per-host 1req/s polite limiter, 15-min in-process TTL
   cache keyed by url+public-params (secret params like app_key excluded from
   the cache key on principle, even though it's in-process only).
   `# ponytail: in-process TTL cache, move to redis if we ever run >1 worker`
3. `apps/api/daari/sources_config.py` — tiny yaml loader for data/sources.yaml
   (myscheme's key lives there).
4. `apps/api/daari/fetchers/{remotive,adzuna,myscheme,nominatim}.py` — each
   `async fetch(...) -> tuple[list[dict], str|None]`, never raises, stamps
   fetched_at ONCE per call (two-clock guard), carries source/source_url/is_live.
5. `apps/api/daari/skills_map.py` — free-text -> skill-id via aliases[], no LLM,
   word-boundary regex, longest-alias-wins on overlapping spans (real example:
   "spreadsheets" vs "advanced spreadsheets").
6. `apps/api/daari/llm/chain.py` — the only LLM entry point. Gemini->Groq->
   Ollama->cache(per-provider, checked before network so offline replay works).
   Disk cache under settings.LLM_CACHE_DIR, sha256(task+model+normalised_input).
   Per-provider breaker: 3 fails or one 429 -> skip 60s. Imports GEMINI_MODEL/
   GROQ_CHAT_MODEL/OLLAMA_MODEL from daari.main (not redeclared).
7. Routes added to routes.py (thin adapters, no scoring logic):
   GET /leads/live, GET /schemes, GET /geocode, POST /match gained `live: bool`.

## Security fix (mid-task, flagged by coordinator)
adzuna.py originally reused the credentialed request URL as source_url
fallback and hand-built the query string. Fixed:
- daari/http.py get_json() now takes `params=` (httpx-encoded, not hand-joined)
  and its cache key drops any param named app_id/app_key/api_key/x-api-key/key.
- adzuna.py source_url is always job['redirect_url'] (Adzuna's own public link)
  or a credential-free `_public_search_url(q)` fallback — never the request URL.
- Added regression tests: test_adzuna_source_url_never_carries_the_credentialed_request_url,
  test_adzuna_request_uses_params_not_a_hand_built_query_string.
Checked myscheme/nominatim/remotive for the same pattern: no leak (myscheme's
key is a header not a URL param; nominatim/remotive carry no credentials at all).

## Tests
apps/api/tests/test_fetchers.py (12 tests, monkeypatches get_json — no respx dep,
no live network), apps/api/tests/test_skills_map.py (6 tests).
`cd apps/api && uv run pytest -q` -> 42 passed (was 25).
`uv run ruff check .` -> All checks passed (after --fix: dropped redundant
.encode("utf-8"), sorted an import block, lambda->dict in a test).

## Live smoke (server on :8010 was already occupied by another builder's/human's
uvicorn — ran mine on :8011 instead, killed it after the smoke test)
- GET /leads/live?q=data%20analyst&limit=3 -> 3 real Adzuna listings (key now
  works — human's re-paste landed mid-task), skills mapped, source_url is
  Adzuna's public redirect link, no credentials in it.
- GET /schemes?q=income&limit=3 -> 3 real myscheme.gov.in schemes.
- GET /geocode?q=Guntur -> real Nominatim lat/lon for Guntur, AP.
- POST /match {live:true} -> live_count 6, seed_count 10, live_errors {},
  merged candidates score correctly through daari_core.match (unmodified).
Not committed (per instructions).
