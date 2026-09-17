"""daari_core.profile — the held-skill vector.

Pure: numpy + stdlib only. Embeddings are always caller-supplied (D18);
daari_core loads no model and touches no network, so a held skill with no
matching embedding is a caller bug and raises rather than defaulting or
silently skipping.
"""

import numpy as np


def vector(held: dict[str, tuple[int, float]], embeddings: dict[str, np.ndarray]) -> tuple[np.ndarray, int]:
    """Weighted mean of held-skill embeddings; weight = level * (1 - se).

    Returns `(vector, version)`. `version` is the number of skills held —
    it moves every time a skill is added, which is what "re-embedded on
    every skill update" needs a caller-visible counter for; daari_core
    keeps no state between calls (core.md determinism), so version is
    derived purely from the `held` snapshot passed in, not from history.
    """
    if not held:
        raise ValueError("profile.vector requires at least one held skill")

    weighted_sum: np.ndarray | None = None
    total_weight = 0.0
    for skill_id, (level, se) in held.items():
        if skill_id not in embeddings:
            raise KeyError(f"no embedding supplied for held skill {skill_id!r} — daari_core loads no model, ever")
        weight = level * (1 - se)
        contribution = weight * embeddings[skill_id]
        weighted_sum = contribution if weighted_sum is None else weighted_sum + contribution
        total_weight += weight

    if total_weight == 0.0:
        raise ValueError("profile.vector: total weight is zero (every held skill has se=1)")

    return weighted_sum / total_weight, len(held)


def cosine_shift(before: np.ndarray, after: np.ndarray, goal: np.ndarray) -> float:
    """How much closer to `goal` the profile moved: cos(after, goal) - cos(before, goal)."""
    return _cosine(after, goal) - _cosine(before, goal)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)
