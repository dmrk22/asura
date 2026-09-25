"""daari.leads — optional locally saved listings.

The application starts with no local listings. Live fetchers may provide cards
at request time; a future import flow can populate ``data/leads`` without
changing the matching engine.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from daari_core.match import Candidate

from daari.taxonomy_loader import get_taxonomy

REPO_ROOT = Path(__file__).resolve().parents[3]
LEADS_FILE = REPO_ROOT / "data" / "leads" / "listings.yaml"


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        parsed = yaml.safe_load(f)
    return parsed or []


@lru_cache(maxsize=1)
def get_candidates() -> tuple[Candidate, ...]:
    """Locally saved listings, validated against the current taxonomy."""
    taxonomy = get_taxonomy()
    candidates: list[Candidate] = []
    for raw in _read(LEADS_FILE):
        required = dict(raw.get("required_skills") or {})
        unknown = sorted(s for s in required if s not in taxonomy.skills)
        if unknown:
            raise ValueError(f"listing {raw['id']!r} references unknown skills: {unknown}")
        candidates.append(
            Candidate(
                id=raw["id"],
                title=raw["title"],
                org=raw["org"],
                location=raw["location"],
                required_skills=required,
                source=raw["source"],
                source_url=raw["source_url"],
                fetched_at=raw["fetched_at"],
                pay=raw.get("pay"),
                extra={"is_live": bool(raw.get("is_live", False))},
            )
        )
    return tuple(candidates)
