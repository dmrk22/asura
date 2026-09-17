"""daari.routes — the engine routes.

Every route here is a thin adapter: parse the request, call `daari_core`, shape
the response. No matching, roadmap, ordering or scoring logic lives in this
file — that is CLAUDE.md non-negotiable 1, and `packages/core`'s AST test
enforces it. If you find yourself writing an `if` that changes a score here,
it belongs in the engine.

Both personas go through the same functions. There is no `if persona ==
"rural"` branch anywhere in this module, and the telemetry counter records
which persona asked so `/evidence` can show that both routes hit one engine.
"""

from __future__ import annotations

from typing import Literal

from daari_core import roadmap as roadmap_engine
from daari_core import telemetry
from daari_core.match import Candidate, match
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from daari.leads import get_candidates, get_personas
from daari.taxonomy_loader import get_taxonomy

router = APIRouter()

MAX_DEMAND_INPUT = 100.0


# --- request models ----------------------------------------------------


class RoadmapRequest(BaseModel):
    held: dict[str, int] = Field(default_factory=dict)
    goal: str
    demand: dict[str, float] = Field(default_factory=dict)
    persona: Literal["student", "rural"] = "student"


class LearnRequest(RoadmapRequest):
    skill: str
    level: int = 5


class ShockRequest(RoadmapRequest):
    skill: str
    weight: float = 2.0


class MatchRequest(BaseModel):
    held: dict[str, int] = Field(default_factory=dict)
    districts: list[str] = Field(default_factory=list)
    demand: dict[str, float] = Field(default_factory=dict)
    persona: Literal["student", "rural"] = "student"


# --- shaping -----------------------------------------------------------


def _validate(held: dict[str, int], goal: str | None = None) -> None:
    taxonomy = get_taxonomy()
    unknown = sorted(s for s in held if s not in taxonomy.skills)
    if unknown:
        raise HTTPException(422, f"unknown skill ids: {unknown}")
    bad_levels = sorted(s for s, lvl in held.items() if not 0 <= lvl <= 5)
    if bad_levels:
        raise HTTPException(422, f"levels must be 0-5: {bad_levels}")
    if goal is not None and goal not in taxonomy.roles:
        raise HTTPException(404, f"unknown goal role: {goal!r}")


def _path_json(path: roadmap_engine.Path) -> dict:
    return {
        "goal": path.goal,
        "goal_label_en": path.goal_label_en,
        "goal_label_te": path.goal_label_te,
        "total_hours": path.total_hours,
        "weeks_at_10hpw": round(path.weeks_at(10), 1) if path.total_hours else 0.0,
        "steps": [
            {
                "skill": s.skill,
                "label_en": s.label_en,
                "label_te": s.label_te,
                "label_hi": s.label_hi,
                "hours": s.hours,
                "level": s.level,
                "prereqs": list(s.prereqs),
                "why": list(s.why),
                "source": s.source,
                "demand": s.demand,
            }
            for s in path.steps
        ],
    }


def _diff_json(d: roadmap_engine.Diff) -> dict:
    return {
        "removed": list(d.removed),
        "added": list(d.added),
        "reordered": list(d.reordered),
        "hours_delta": d.hours_delta,
        "cause": d.cause,
        "empty": d.is_empty(),
    }


def _candidate_json(c: Candidate) -> dict:
    return {
        "id": c.id,
        "title": c.title,
        "org": c.org,
        "location": c.location,
        "pay": c.pay,
        "required_skills": c.required_skills,
        # Provenance travels with every listing, always. rules/safety.md guard 2.
        "source": c.source,
        "source_url": c.source_url,
        "fetched_at": c.fetched_at,
        "is_live": c.extra.get("is_live", False),
    }


def _clean_demand(demand: dict[str, float]) -> dict[str, float]:
    taxonomy = get_taxonomy()
    unknown = sorted(s for s in demand if s not in taxonomy.skills)
    if unknown:
        raise HTTPException(422, f"demand references unknown skill ids: {unknown}")
    bad = sorted(s for s, w in demand.items() if not 0 < w <= MAX_DEMAND_INPUT)
    if bad:
        raise HTTPException(422, f"demand weights must be in (0, {MAX_DEMAND_INPUT}]: {bad}")
    return demand


# --- routes ------------------------------------------------------------


@router.get("/taxonomy")
def taxonomy() -> dict:
    tx = get_taxonomy()
    return {
        "skills": [
            {
                "id": n.id,
                "label_en": n.label_en,
                "label_te": n.label_te,
                "label_hi": n.label_hi,
                "level": n.level,
                "hours": n.hours,
                "prereqs": list(n.prereqs),
                "source": n.source,
            }
            for n in sorted(tx.skills.values(), key=lambda n: n.id)
        ],
        "roles": [
            {
                "id": r.id,
                "label_en": r.label_en,
                "label_te": r.label_te,
                "label_hi": r.label_hi,
                "required_skills": r.required_skills,
                "source": r.source,
            }
            for r in sorted(tx.roles.values(), key=lambda r: r.id)
        ],
        "counts": {"skills": len(tx.skills), "roles": len(tx.roles)},
    }


@router.get("/personas")
def personas() -> dict:
    return {
        "personas": [
            {
                "id": p.id,
                "name": p.name,
                "persona": p.persona,
                "goal": p.goal,
                "held": p.held,
                "districts": list(p.districts),
                "district": p.district,
                "languages": list(p.languages),
                "note": p.note,
                "synthetic": True,
            }
            for p in get_personas().values()
        ]
    }


@router.post("/roadmap")
def build_roadmap(req: RoadmapRequest) -> dict:
    _validate(req.held, req.goal)
    demand = _clean_demand(req.demand)
    telemetry.count(req.persona, "roadmap")
    path = roadmap_engine.compute(get_taxonomy(), held=req.held, goal=req.goal, demand=demand)
    return {"path": _path_json(path), "persona": req.persona}


@router.post("/roadmap/learn")
def learn_skill(req: LearnRequest) -> dict:
    """The learner marks a skill learned. Returns before, after and the diff —
    the §6 P2 gate's 'Before | After' beat."""
    _validate(req.held, req.goal)
    _validate({req.skill: req.level})
    demand = _clean_demand(req.demand)
    telemetry.count(req.persona, "roadmap_learn")

    tx = get_taxonomy()
    before = roadmap_engine.compute(tx, held=req.held, goal=req.goal, demand=demand)
    after_held = {**req.held, req.skill: max(req.held.get(req.skill, 0), req.level)}
    after = roadmap_engine.compute(tx, held=after_held, goal=req.goal, demand=demand)
    diff = roadmap_engine.diff(before, after, cause="learner")

    return {
        "before": _path_json(before),
        "after": _path_json(after),
        "diff": _diff_json(diff),
        "held_after": after_held,
        "persona": req.persona,
    }


@router.post("/roadmap/shock")
def market_shock(req: ShockRequest) -> dict:
    """The judge's Market shock control: raise one skill's demand and re-route.

    The demand weight is clamped inside the engine (§7.3 caps it at 2x), so a
    large `weight` here cannot produce a dramatic-but-fake reordering.
    """
    _validate(req.held, req.goal)
    _validate({req.skill: 0})
    demand = _clean_demand({**req.demand, req.skill: req.weight})
    telemetry.count(req.persona, "roadmap_shock")

    tx = get_taxonomy()
    before = roadmap_engine.compute(tx, held=req.held, goal=req.goal, demand=req.demand)
    after = roadmap_engine.compute(tx, held=req.held, goal=req.goal, demand=demand)
    diff = roadmap_engine.diff(before, after, cause="market")

    return {
        "before": _path_json(before),
        "after": _path_json(after),
        "diff": _diff_json(diff),
        "shocked_skill": req.skill,
        "applied_weight": min(req.weight, roadmap_engine.MAX_DEMAND),
        "requested_weight": req.weight,
        "persona": req.persona,
    }


@router.post("/match")
def match_leads(req: MatchRequest) -> dict:
    _validate(req.held)
    demand = _clean_demand(req.demand)
    telemetry.count(req.persona, "match")

    candidates = get_candidates()
    results = match(
        get_taxonomy(),
        held=req.held,
        candidates=list(candidates),
        demand=demand,
        districts=tuple(req.districts),
    )
    by_id = {c.id: c for c in candidates}
    return {
        "matches": [
            {
                **_candidate_json(by_id[m.candidate_id]),
                "match_score": m.score,
                "components": m.components,
                "missing_skills": list(m.missing),
                "reasons": list(m.reasons),
            }
            for m in results
        ],
        "count": len(results),
        "live": False,
        "provenance_note": (
            "Seed listings, not a live fetch. Every card keeps its source and fetched_at. "
            "Live fetchers (Adzuna / Remotive / SerpAPI) land in P3."
        ),
        "persona": req.persona,
    }


@router.get("/evidence")
def evidence() -> dict:
    """What the shared engine actually did, per persona — the import-graph claim
    backed by live call counters rather than an assertion in a slide."""
    tx = get_taxonomy()
    return {
        "shared_engine": {
            "package": "daari_core",
            "calls_by_persona": telemetry.snapshot(),
            "note": "Both persona routes call the same daari_core functions; no route holds its own matcher.",
        },
        "taxonomy": {"skills": len(tx.skills), "roles": len(tx.roles)},
        "leads": {"count": len(get_candidates()), "live": False},
    }
