# DEMO.md — the 6:45 script (persona Ravi)

Filled during P8 rehearsal. Every LLM call named here is pre-executed by `scripts/warm_cache.py`
and answered from cache, so the scripted path runs with the network unplugged.

| # | t | Screen | Beat | Cached call? |
|---|---|---|---|---|
| 1 | 0:00 | `/` | "Team ASURA. NADI: one agent, five engines, every answer traceable." Counter → Open demo | no |
| 2 | 0:30 | `/today` | "Can I do HIIT this week? And what should dinner look like?" → mode `wellness`, plan, **constraint trace** opens: `BB-02` RPE not HR zones, `HTN-01` sodium cap, `T2D-03` glucose check | yes |
| 3 | 1:45 | `/meals` | Drop the dal-rice-roti photo → 3 dishes. Tap roti 2→3 → ranges recompute instantly. "No model call — the numbers come from IFCT tables." | yes (vision) |
| 4 | 3:00 | `/vitals` | 60× time-scale. Hand the trackpad to a mentor: "Pick an anomaly." `nocturnal_hypoglycemia` → CGM drops → alert under a second; HUD shows latency; mode chip flips to `escalated` | no |
| 5 | 4:15 | `/today` | Urgency card already present. Type "I feel shaky and sweaty" → EMERGENCY **via lexicon, no model call**; 112/108 buttons; handoff card | no |
| 6 | 5:30 | `/evidence` | Router held-out accuracy, red-flag recall 100%, adversarial violations 0, p95 latency, tests passing, provider mix, CI sha. "Not a claim. CI output." | no |
| 7 | 6:15 | — | Close: five engines, local-first, ₹0 stack, QR if deployed. **Stop at 6:45.** | no |

## Prepared answers (§11)
- **Why not BioMistral / Med-PaLM?** Med-PaLM isn't available. BioMistral is a 7B research model that
  hallucinates guidelines. We retrieve real WHO/NHS/ICMR text and cite it; the model only frames.
  Open models are in the chain — Llama via Groq, Qwen via Ollama.
- **Why not LLaVA?** Gemini Flash and Llama 4 vision beat it on food and cost nothing. And the model only
  identifies dishes and portions — the macros are table lookups.
- **Why not Kafka/Flink?** Same semantics (append log, consumer groups) in one binary, one adapter to swap.
  Correct demo over a logo.
- **Why no React Native?** Every screen works at 390 px. A mobile app costs hours we spent on the detector.
- **Deterministic?** Tiers 1–2 fully — regex, then fixed-seed logistic regression on frozen embeddings.
  Tier 3 fires on under 5% of inputs at temperature 0, cached and logged. The tier column shows which decided.
- **Macro accuracy?** An 8-photo eval with the honest number on screen. Ranges, not points. Portions
  corrected in household units.
- **What stops a diagnosis?** The schema has no field for one. Then the guard: regex → rewrite → template.
  Adversarial eval sits at 0. Try it yourself.
- **Real data?** None. Synthetic personas and sensors; public-licence corpus with the licence on every citation.
- **Cost to run?** ₹0 today. The provider chain is an interface, so a paid model is a config line.

## QR codes
Written by `/ship` if the optional deploy runs. Laptop demo is the primary.
