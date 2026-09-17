# safety.md — the rules no phase may trade away

- A tier-1 lexicon hit sets urgency **before any model call**. Nothing downstream lowers it. `escalate()` is `max()` across lexicon, vitals, profile multipliers and model suggestion — never `min`, never "override".
- The triage response schema has **no field for a diagnosis**. If you find yourself adding one, the answer is no.
- Every triage and coach reply passes `triage.guard`. Violation → one rewrite at temperature 0 quoting the violation → still violating → the pre-written cited template for that urgency level. There is no third path and no bypass flag.
- Suicidal ideation → EMERGENCY, Tele-MANAS 14416 + 112, supportive script. No method discussion. No further detail. Ever.
- CI gates, non-negotiable: red-flag recall = 1.00 on the 60-item set; adversarial-diagnosis violations = 0 on the 40-item set; router held-out accuracy ≥ 0.93. A red safety eval blocks every merge and every deploy.
- Anything derived from an image is a **range with a confidence**, never a point.
- Synthetic personas and synthetic sensors only. No real health data enters this repo.
- Every citation carries `{title, url, license}`. Nothing paywalled, nothing uncited.
