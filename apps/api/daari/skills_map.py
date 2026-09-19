"""daari.skills_map — deterministic free-text -> taxonomy skill-id mapping.

No LLM (CLAUDE.md non-negotiable 3): a live listing's title/description is
matched against each skill's `aliases[]` from `data/taxonomy/skills.yaml` via
case-insensitive, word-boundary regex. Longest-alias-wins: when one skill's
alias is itself a substring of another skill's alias (e.g. "spreadsheets"
inside "advanced spreadsheets"), the longer, more specific alias claims that
span and the shorter one is not also counted for it.

This is what lets a live Remotive/Adzuna listing reach `daari_core.match()`,
whose `required_skills` must be taxonomy ids.

A listing never states a required proficiency level, so every mapped skill
is assigned the same default required level (3 of 5) — a stated assumption,
not an extracted fact.
"""

from __future__ import annotations

import re

from daari.taxonomy_loader import get_taxonomy

DEFAULT_REQUIRED_LEVEL = 3


def map_text_to_skills(text: str) -> dict[str, int]:
    """Free text -> `{skill_id: DEFAULT_REQUIRED_LEVEL}` for every taxonomy
    skill whose alias appears in `text`, word-boundary and case-insensitive,
    longest-alias-wins on overlapping spans."""
    taxonomy = get_taxonomy()
    terms: list[tuple[str, str]] = [
        (alias, skill_id) for skill_id, node in taxonomy.skills.items() for alias in node.aliases if alias
    ]
    # Longest alias first so a longer, more specific phrase claims its span
    # in `text` before a shorter alias nested inside it can also claim it.
    terms.sort(key=lambda t: len(t[0]), reverse=True)

    matched: dict[str, int] = {}
    claimed: list[tuple[int, int]] = []
    for alias, skill_id in terms:
        if skill_id in matched:
            continue
        m = re.search(rf"\b{re.escape(alias)}\b", text, re.IGNORECASE)
        if not m:
            continue
        start, end = m.span()
        if any(start < c_end and end > c_start for c_start, c_end in claimed):
            continue
        claimed.append((start, end))
        matched[skill_id] = DEFAULT_REQUIRED_LEVEL
    return matched
