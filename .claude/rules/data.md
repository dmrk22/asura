# data.md — data/ and evals/

- `data/taxonomy/skills.yaml`: ~300 nodes, each `{id, label_en, label_te, label_hi, aliases[], level 1–5, hours, source}`. Sources: NSQF descriptors, NCO-2015, ESCO labels, Skill India / NPTEL free-course names. **A node without a source is not a node.** Telugu and Hindi labels are LLM-generated at temperature 0 and reviewed by the data lane (or by TTS read-back if no Telugu speaker is present).
- `data/taxonomy/roles.yaml`: ~40 roles, each a set of required skill ids with required levels.
- `data/items/items.yaml`: the CAT item bank. ≥ 8 items × 3 difficulty bands (b ∈ {−1, 0, +1}) for the 12 skills across the two demo roles, plus 60 generic (spoken English, basic numeracy, digital literacy). Each item carries a source or a stated rationale. Difficulty bands are **stated assumptions, not empirical calibrations** — say so in the pitch and in `docs/DECISIONS.md`. The data lane spot-checks 20.
- `data/sources.yaml`: every live source with its licence / ToS note. Adzuna India, Remotive, SerpAPI Google Jobs (budgeted), myscheme.gov.in, AP scheme pages. Nothing paywalled. The source and fetch time are shown on every card in the UI.
- `data/personas/`: Ravi, Priya, blank. Synthetic. No real person, no real record. Real live leads, fake people.
- Corpus and fetch caches are **idempotent and resumable** — re-running a fetch must not duplicate rows.
- Eval sets are append-only and never trimmed to make a number look better. If an eval gets easier, say so in `docs/DECISIONS.md`.
- Eval sets and their CI thresholds (§10):
  | File | Size | Threshold |
  |---|---|---|
  | `schemes_golden.jsonl` | 40 (half Telugu) | precision@5 ≥ 0.8 |
  | `roadmap_cases.jsonl` | 20 (8 market-shock) | invariants pass |
  | `match_pairs.jsonl` | 40 | graph-on ≥ graph-off |
  | `scam_golden.jsonl` | 30 (15 scam / 15 clean) | recall ≥ 0.9, precision ≥ 0.8 |
  | `feedback_golden.jsonl` | 20 | must-mention recall ≥ 0.8 |
  | `feedback_adversarial.jsonl` | 30 | violations = 0 |
  | `voice_latency.py` | 10 clips | first audio p95 < 1.5 s, total p95 < 4 s |
- A red eval blocks every merge and every deploy.
- Demo audio clips live in `evals/voice/clips/` (gitignored) with transcripts in a committed JSONL — the transcripts are the eval, the audio is the demo.
