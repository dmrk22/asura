# P2 — engine: graph, vectors, matcher, roadmap + Before | After, CAT, tool registry

## 1. Gate

§6 is the repo layout; it carries no gate rows. The definition of done is §13's P2 row plus the §6 file list for the modules it names, verbatim:

> §13: "P2 engine (graph, vectors, matcher, roadmap + Before \| After, CAT, tool registry)"
>
> §6: `packages/core/daari_core/` — `graph.py taxonomy.py profile.py match.py roadmap.py demand.py eligibility.py assess.py` … `apps/api/daari/ agent/ loop.py registry.py trace.py` … `data/ taxonomy/skills.yaml roles.yaml items/items.yaml`

**In this phase:** `taxonomy.py graph.py profile.py match.py roadmap.py demand.py assess.py`, `agent/registry.py`, seed `data/taxonomy/{skills,roles}.yaml` + `data/items/items.yaml`.
**Not in this phase** (do not overreach): `eligibility.py scam.py geo.py constitution.py prep.py interview_metrics.py` (P3/P5), `agent/loop.py` + `agent/trace.py` + the LLM provider chain (P4, §7.10/§7.15), any live fetching (P3 — demand is a plain argument, so the 401'd `ADZUNA_APP_KEY`/`SERPAPI_KEY` do not block P2).

**Gate is met when:** `cd packages/core && uv run pytest -q` and `cd apps/api && uv run pytest -q` are green with every §2 test present and named as below; `test_purity`, `test_shared_engine` (both cases, fixture included) and `test_telemetry` still pass unweakened; `/health`'s `tools` count is > 0 and equals the registry length.

**Two decisions this plan makes, to be logged as D17/D18 in `docs/DECISIONS.md` (task T14):**
- **D17 — seed taxonomy in the real files, not an in-test fixture.** `data/` does not exist yet. P2 writes a small real seed (≈24 skill nodes covering the two demo roles' 12 skills plus their prerequisites and two adjacency pairs; 2 roles — Priya → Data Analyst, Ravi → one local gig role from §7.6's list, data lane picks; ≥ 8 items × 3 bands for 2 skills + 8 generic). Every node carries a real source (NSQF QP/NOS code, NCO-2015 code, ESCO URI, or a Skill India / NPTEL course URL) — a node without a source is not a node, seed size included. Growth to 300 skills / 40 roles / the full bank is P3+ data-lane work. Core tests load the real seed files, so the file format is proven by the algorithms that consume it.
- **D18 — embeddings are a committed deterministic fixture in P2.** `daari_core` never loads a model or touches the network; embeddings are caller-supplied arrays. P2 supplies them from `packages/core/tests/fixtures/embeddings.py`: `numpy.random.default_rng(sha256(skill_id))` per id, with a handful of hand-set near-duplicate pairs (e.g. Tableau ↔ Power BI) forced above and below cosine 0.75 so the adjacency threshold is exercised in both directions. Real multilingual embeddings + pgvector arrive with the app-layer caller in P3. Determinism of the fixture is itself asserted.

## 2. Acceptance tests (written before any implementation task)

| Test (file :: name) | Proves |
|---|---|
| `tests/test_taxonomy.py::test_every_skill_node_has_a_source` | data.md — a node without a source is not a node |
| `…::test_every_node_has_en_te_hi_labels` | CLAUDE.md #12 / §7.1 node schema |
| `…::test_roles_reference_only_known_skill_ids_with_levels` | §7.1 / data.md roles.yaml |
| `…::test_taxonomy_builds_from_parsed_dicts_without_io` | core.md purity — YAML parsing is the caller's job |
| `tests/test_graph.py::test_prereq_edge_weight_is_hours` | §7.1 |
| `…::test_adjacency_edge_iff_cosine_ge_0_75_and_weight_is_0_3_hours` | §7.1 (fixture forces both sides of the threshold) |
| `…::test_transferability_edge_iff_pmi_ge_1_and_count_ge_5_weight_hours_times_1_minus_min_pmi_over_3_0_5` | §7.1 |
| `…::test_edges_added_today_is_counted_not_hardcoded` | §7.1 / safety.md #2 |
| `…::test_graph_build_is_deterministic_under_permuted_input` | core.md — determinism, stable tie-break |
| `tests/test_profile.py::test_vector_is_weighted_mean_with_weight_level_times_one_minus_se` | §7.2 |
| `…::test_cosine_shift_toward_goal_is_non_negative_after_learning_a_required_skill` | core.md v6 invariant |
| `…::test_vector_version_increments_on_every_skill_update` | §7.2 |
| `…::test_core_requires_caller_supplied_embeddings` (raises, never fetches) | core.md — core loads no model |
| `tests/test_match.py::test_match_returns_all_five_components` (`coverage, gap_cost, constraint_fit, demand_bonus, vector_sim`) | core.md — every score decomposed |
| `…::test_score_is_the_weighted_sum_of_its_components` (0.4·cov − 0.2·gap + 0.15·vec + 0.15·fit + 0.10·demand) | §7.3 |
| `…::test_coverage_uses_the_cat_lower_bound_not_the_point_estimate` | §7.3 |
| `…::test_gap_cost_is_shortest_path_hours_over_all_three_edge_types_normalised` | §7.3 |
| `…::test_missing_surplus_and_reasons_are_populated` | §7.3 / Constitution VI |
| `…::test_ablation_graph_on_ge_graph_off` and `…::test_ablation_vector_on_ge_vector_off` | §7.3/§10 — ablations are engine calls with components disabled, not hand-tuned. P2 asserts the mechanism on a 6-pair seed; the 40-pair `match_pairs.jsonl` threshold is P3+. |
| `tests/test_roadmap.py::test_learning_a_required_skill_never_lengthens_the_path` (hypothesis) | core.md invariant |
| `…::test_demand_increase_never_moves_that_skill_later` (hypothesis) | core.md v6 invariant / §7.4 market shock |
| `…::test_diff_of_identical_paths_is_empty` | core.md — `diff(x, x)` is empty |
| `…::test_steps_are_topologically_ordered_and_every_step_has_why` | §7.4 |
| `…::test_diff_reports_cause_learner_or_market_and_hours_delta` | §7.4 Before \| After |
| `…::test_demand_weight_is_one_plus_log1p_share_times_ten_capped_at_two` | §7.4 |
| `…::test_roadmap_is_deterministic_under_permuted_input` | core.md determinism |
| `tests/test_assess.py::test_se_decreases_monotonically` | §7.7 / core.md Rasch invariants |
| `…::test_all_correct_respondent_ends_at_theta_ge_plus_one` | §7.7 |
| `…::test_stopping_rule_always_terminates` (hypothesis over response patterns; SE < 0.4 or 6 items) | §7.7, §10 CAT termination gate |
| `…::test_item_selection_maximises_information_at_current_theta` | §7.7 |
| `…::test_theta_maps_to_level_1_5_carrying_se_as_the_error_bar` | §7.7 → §7.2 held[skill] = (level, se) |
| `…::test_assess_reads_no_clock_and_takes_its_seed_as_an_argument` | core.md determinism |
| `apps/api/tests/test_registry.py::test_registry_exposes_the_p2_engine_tools` (`get_profile, update_skill, assess_next_item, get_roadmap, simulate_skill_update, market_shock, match_leads`) | §7.10 |
| `…::test_every_tool_arg_and_return_is_a_pydantic_v2_model` | §7.10 / api.md |
| `…::test_registry_contains_no_engine_logic` (AST: no engine-named defs, no score arithmetic) | CLAUDE.md #1, mirrors `test_shared_engine` |
| `…::test_registry_makes_no_llm_call_and_runs_no_loop` | scope fence — the loop is P4 |
| `…::test_student_and_rural_personas_get_identical_engine_output` | core.md — both persona adapters identical on identical input |
| `…::test_every_tool_call_increments_telemetry` | telemetry.py, `/evidence` reads the live process |
| `…::test_health_tools_count_equals_registry_length` | STATE.md P1 row "count 0 until P2" |

## 3. Tasks

Lanes: **D** = `data/`, **C** = `packages/core/`, **A** = `apps/api/`. Tasks in different lanes are parallel-safe (max 3 builders, CLAUDE.md).

| # | Task (≤ 45 min) | Files | Lane / parallel-safe |
|---|---|---|---|
| T0 | Seed `skills.yaml` (≈24 nodes: id, label_en/te/hi, aliases, level, hours, source, prereqs) + `roles.yaml` (2 roles → required skill ids + levels) | `data/taxonomy/skills.yaml`, `data/taxonomy/roles.yaml` | D — parallel-safe |
| T0b | Seed `items.yaml`: ≥ 8 items × b ∈ {−1,0,+1} for 2 skills + 8 generic; each item a source or a stated rationale; band assumption stated | `data/items/items.yaml` | D — parallel-safe (after T0's ids) |
| T1 | Freeze the entry-point signatures in this plan's appendix so lanes C and A can start together; add `pyyaml` to core's **dev** group only (runtime stays numpy+networkx+stdlib); test loader + `seeded_embedding()` fixture | `packages/core/pyproject.toml`, `tests/conftest.py`, `tests/fixtures/embeddings.py` | C — parallel-safe |
| T2 | Failing tests: taxonomy + graph (rows 1–9) | `packages/core/tests/test_taxonomy.py`, `test_graph.py` | C |
| T3 | Implement `taxonomy.py` + `graph.py` | `packages/core/daari_core/taxonomy.py`, `graph.py` | C |
| T4 | Failing tests: profile/vectors (rows 10–13) | `packages/core/tests/test_profile.py` | C |
| T5 | Implement `profile.py` | `packages/core/daari_core/profile.py` | C |
| T6 | Failing tests: matcher (rows 14–19) | `packages/core/tests/test_match.py` | C |
| T7 | Implement `match.py` with components toggleable by argument (ablation is an engine call) | `packages/core/daari_core/match.py` | C |
| T8 | Failing tests: demand + roadmap + diff, hypothesis (rows 20–26) | `packages/core/tests/test_roadmap.py` | C |
| T9 | Implement `demand.py` + `roadmap.py` (Dijkstra on hours/demand, merge, topo order, `why[]`, `diff()`) | `packages/core/daari_core/demand.py`, `roadmap.py` | C |
| T10 | Failing tests: CAT (rows 27–32) | `packages/core/tests/test_assess.py` | C |
| T11 | Implement `assess.py` (Rasch 1PL, max-information selection, Newton–Raphson, SE = 1/√ΣI, stop at SE < 0.4 or 6) | `packages/core/daari_core/assess.py` | C |
| T12 | Failing tests: tool registry (rows 33–39) against the T1 signatures | `apps/api/tests/test_registry.py` | A — parallel-safe from T1 |
| T13 | Implement `agent/registry.py` (typed thin wrappers → `daari_core`, telemetry per call) + wire `/health` `tools` count | `apps/api/daari/agent/__init__.py`, `registry.py`, `apps/api/daari/main.py` | A — parallel-safe with C |
| T14 | `docs/DECISIONS.md` D17 (seed taxonomy) + D18 (fixture embeddings) + P2 row in `docs/STATE.md` | `docs/DECISIONS.md`, `docs/STATE.md` | — (integrator, last) |
| T15 | Full suite: core pytest, api pytest, ruff both; record results in STATE.md; conventional commit | — | — (integrator, last) |

**Appendix — signatures frozen at T1** (so lanes C and A cannot drift; no bodies):
`taxonomy.load(skills: list[dict], roles: list[dict]) -> Taxonomy` · `graph.build(taxonomy, embeddings: dict[str, ndarray], pmi: dict[tuple[str,str], tuple[float,int]] | None) -> Graph` · `profile.vector(held: dict[str, tuple[int,float]], embeddings) -> tuple[ndarray, int]` · `profile.cosine_shift(before: ndarray, after: ndarray, goal: ndarray) -> float` · `match.match(profile, candidates, graph, demand, components: set[str] | None) -> list[Match]` · `demand.demand(listings_by_district) -> dict[str, float]` · `roadmap.roadmap(profile, goal, demand, graph) -> Path` · `roadmap.diff(before: Path, after: Path, cause: str) -> Diff` · `assess.next_item(theta, se, items, asked) -> Item | None` · `assess.update(theta, item, correct) -> tuple[float, float]`.

## 4. Cut line

On a 15-minute overrun, in this order:

1. **§13 cut 10 — transferability edges → adjacency only.** `graph.build` accepts `pmi=None` and builds prereq + adjacency edges only; `edges_added_today` reports 0 with the reason "transferability off", never a hidden number. Gap cost still uses shortest path over the two remaining edge types, so the graph-on/graph-off ablation still holds.
2. **§13 cut 7 — CAT → fixed 6-question quiz.** `assess` keeps its Rasch scoring for `theta`/`se` but selects a fixed 6-item sequence instead of maximising information. `test_stopping_rule_always_terminates` and `test_se_decreases_monotonically` must still pass; only `test_item_selection_maximises_information_at_current_theta` is skipped, with a reason and a DECISIONS entry.

**Never cut in this phase** (§13 never-cut list): `packages/core` + its tests, the AST shared-engine test, the demand-weighted roadmap with Before \| After and "Simulate skill update", the profile vector shift. If time runs out after cut 2, ship what is green, log the gap in `docs/STATE.md`, and move to P3 — no slot extension without a `docs/DECISIONS.md` entry (CLAUDE.md #9).
