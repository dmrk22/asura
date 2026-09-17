"""daari.leads — candidate listings and personas, loaded from committed data.

Like `taxonomy_loader`, all I/O lives here rather than in `daari_core`.

Everything this module returns is **seed data, not live**. Each listing keeps
its `source`, `source_url`, `fetched_at` and an explicit `is_live: False`, and
the routes pass all four through untouched. rules/safety.md guard 2 permits a
snapshot only with the stamp visible, so nothing here may be rendered as a live
fetch. The P3 fetchers replace `_read_jobs`; the `Candidate` shape stays.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from daari_core.match import Candidate

from daari.taxonomy_loader import get_taxonomy

REPO_ROOT = Path(__file__).resolve().parents[3]
LEADS_FILE = REPO_ROOT / "data" / "leads" / "seed_jobs.yaml"
PERSONAS_FILE = REPO_ROOT / "data" / "personas" / "personas.yaml"


@dataclass(frozen=True)
class Persona:
    id: str
    name: str
    persona: str
    goal: str
    held: dict[str, int]
    districts: tuple[str, ...]
    district: str | None
    languages: tuple[str, ...]
    note: str


def _read(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"seed data missing: {path}")
    with path.open("r", encoding="utf-8") as f:
        parsed = yaml.safe_load(f)
    if not parsed:
        raise ValueError(f"seed data is empty: {path}")
    return parsed


@lru_cache(maxsize=1)
def get_candidates() -> tuple[Candidate, ...]:
    """Seed listings as `Candidate`s, validated against the live taxonomy.

    A listing referencing an unknown skill id raises at load rather than at
    match time — a broken seed file should fail the process on the first
    request, not quietly rank one listing lower than it should.
    """
    taxonomy = get_taxonomy()
    candidates: list[Candidate] = []
    for raw in _read(LEADS_FILE):
        required = dict(raw.get("required_skills") or {})
        unknown = sorted(s for s in required if s not in taxonomy.skills)
        if unknown:
            raise ValueError(f"seed listing {raw['id']!r} references unknown skills: {unknown}")
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


@lru_cache(maxsize=1)
def get_personas() -> dict[str, Persona]:
    taxonomy = get_taxonomy()
    personas: dict[str, Persona] = {}
    for raw in _read(PERSONAS_FILE):
        held = dict(raw.get("held") or {})
        unknown = sorted(s for s in held if s not in taxonomy.skills)
        if unknown:
            raise ValueError(f"persona {raw['id']!r} holds unknown skills: {unknown}")
        if raw["goal"] not in taxonomy.roles:
            raise ValueError(f"persona {raw['id']!r} has unknown goal {raw['goal']!r}")
        constraints = raw.get("constraints") or {}
        personas[raw["id"]] = Persona(
            id=raw["id"],
            name=raw["name"],
            persona=raw["persona"],
            goal=raw["goal"],
            held=held,
            districts=tuple(constraints.get("districts") or ()),
            district=raw.get("district"),
            languages=tuple(raw.get("languages") or ()),
            note=raw.get("note", ""),
        )
    return personas
