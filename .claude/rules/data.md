# data.md — data/ and evals/

- `data/corpus/manifest.yaml`: one entry per document, `{title, url, license}`. WHO, NHS (Open Government Licence), MoHFW/ICMR public PDFs, CDC. Nothing paywalled. The licence is shown on every citation in the UI.
- Corpus build is **idempotent and resumable** — re-running it must not duplicate chunks. Chunk 400 tokens / 60 overlap.
- `data/nutrition/indian_dishes.csv`: per-100 g kcal, protein, carb, fat, fibre, sodium, potassium, sugar, GI band, plus `source` and (for composite dishes) `basis` with the recipe. IFCT 2017 where a dish maps to a food item; USDA FoodData Central otherwise. A row without a source is not a row.
- `data/nutrition/measures.csv`: household units — roti 40 g, katori 150 ml, small spoon 5 ml, glass 200 ml, idli 40 g, dosa 80 g, samosa 100 g, cup chai 150 ml.
- `data/personas/`: Ravi, Priya, Arjun, blank. Synthetic. No real person, no real record.
- Eval sets are append-only and never trimmed to make a number look better. If an eval gets easier, say so in `docs/DECISIONS.md`.
- Meal photos live in `evals/meals/photos/` (gitignored) with labels in a committed JSONL — the labels are the eval, the images are the demo.
