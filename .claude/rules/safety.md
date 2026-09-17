# safety.md — the guards no phase may trade away

These five hold from P1 to `/ship`. A cut line may reduce an engine's sophistication; it may never remove a guard.

## 1. The LLM never decides
Matching, roadmap, eligibility, ability estimate, scam score and interview metrics are deterministic `daari_core` calls. The LLM orchestrates (tool calls), extracts structure at temperature 0 (cached), and writes words. **A test compares every number in the agent's final reply against the tool trace** — a number with no tool result behind it fails the build. There is no bypass flag.

## 2. Provenance or it doesn't ship
Every job and every scheme carries `{source, source_url, fetched_at}` and the UI renders the source and the age. A repo-scan test forbids lead literals outside `tests/fixtures/` and `mocks/`. Snapshots are allowed for the offline demo **only with the stamp visible and "stale since" shown**.

## 3. Scam Shield always states its reasons
`scam_score(listing) -> (score, reasons[])`. A badge without reasons is a bug. ≥ 0.5 → red with reasons; 0.3–0.5 → amber ("check this"), never a silent block. Precision and recall from `scam_golden.jsonl` are on `/evidence` — we show the false-positive rate rather than hiding it.

## 4. No praise without a quote
Every interview feedback item carries a verbatim substring of the candidate's own transcript. `interview/guard.py`: violation → one rewrite at temperature 0 quoting the violation → still violating → the metrics-only template. No third path. `feedback_adversarial.jsonl` violations = 0.

## 5. Eligibility has three states, not two
`evaluate()` returns `True | False | Unknown` with reasons and `missing_fields`. **`Unknown` never renders as "qualifies".** It renders as one question, asked in the user's language. Every predicate stores the snippet that justifies it.

## Data and people
Synthetic personas only — Ravi, Priya, blank. Real live leads, fake people. No real person's data enters this repo. Nothing paywalled, nothing uncited.

## CI gates, non-negotiable (§10)
scheme precision@5 ≥ 0.8 · roadmap invariants pass · scam recall ≥ 0.9 · match ablation graph-on ≥ graph-off · feedback adversarial = 0 · must-mention recall ≥ 0.8 · voice first-audio p95 < 1.5 s and total p95 < 4 s on cached clips · CAT termination test passes.
A red eval blocks every merge and every deploy.

## 6. The Constitution is code, not a slide (v6, §7.13)
`docs/CONSTITUTION.md` has 13 articles; each has a test. Every user-facing factual sentence passes `grounding/verifier.py` before rendering **and** before TTS. A sentence that fails is removed, not rephrased. Every number passes `constitution.check_numbers()`, every date `check_dates()`, every entity `check_names()`.

## 7. Model memory is not a source
Anything time-bound — jobs, schemes, questions, companies, dates, salaries, deadlines, eligibility — is answered only from an evidence bundle with `fetched_at` stamps. The prompt states today's date and forbids recall. A claim dated later than any evidence is struck. A question about a date newer than all evidence returns "our data ends on <date>", the newest data, and no fill-in.

## 8. "No data" is a success path
Absent or thin evidence renders the no-data template: what was searched, the nearest data with its date, one next step. Thin data is labelled on every card. The no-data rate is public on `/evidence`. `nodata_adversarial.jsonl` violations = 0.

## 9. Scope and seriousness
No placement promises, no ranking a person against others, no invented hiring policies or cut-offs. A reported question is labelled "reported by a candidate on <date>". Never instruct a user to pay to apply. Enforced by forbidden-claim regexes in the verifier, not by prompt wording.

## 10. Failure mode
If the verifier itself fails, degrade to structured cards with no free prose. Never ship unverified prose because the verifier was down.
