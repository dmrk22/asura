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

from datetime import UTC, date, datetime
from typing import Any, Literal

from daari_core import assess as assess_engine
from daari_core import eligibility as eligibility_engine
from daari_core import interview as interview_engine
from daari_core import prep as prep_engine
from daari_core import roadmap as roadmap_engine
from daari_core import scam as scam_engine
from daari_core import telemetry
from daari_core.match import Candidate, match
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from daari.fetchers import adzuna as adzuna_fetcher
from daari.fetchers import myscheme as myscheme_fetcher
from daari.fetchers import nominatim as nominatim_fetcher
from daari.fetchers import remotive as remotive_fetcher
from daari.items_loader import get_item_bank
from daari.leads import get_candidates, get_personas
from daari.skills_map import map_text_to_skills
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
    live: bool = False


class AssessStateModel(BaseModel):
    """The CAT session state travels with the client, same pattern as
    `held` on the roadmap routes — no server-side session table needed for
    this hour's scope."""

    theta: float = 0.0
    se: float | None = None
    answered: list[tuple[str, bool]] = Field(default_factory=list)


class AssessNextRequest(BaseModel):
    state: AssessStateModel | None = None
    skill_id: str | None = None
    persona: Literal["student", "rural"] = "student"


class AssessAnswerRequest(BaseModel):
    state: AssessStateModel
    item_id: str
    given_answer: str
    persona: Literal["student", "rural"] = "student"


class EligibilityRequest(BaseModel):
    """A reviewed, source-tied eligibility AST is evaluated only by core."""

    rules: dict[str, Any] | None = None
    facts: dict[str, Any] = Field(default_factory=dict)
    source_url: str
    fetched_at: str
    persona: Literal["student", "rural"] = "rural"


class InterviewRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)
    transcript: str = Field(min_length=1, max_length=20_000)
    question_source_url: str = Field(min_length=1, max_length=2_000)
    persona: Literal["student", "rural"] = "student"


class PrepRequest(BaseModel):
    interview_date: date
    focus: list[str] = Field(default_factory=list, max_length=12)
    notice_source_url: str = Field(min_length=1, max_length=2_000)
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
    # Scam Shield (safety.md guard 3): scored from whatever text the listing
    # actually carries (title/org/pay/source_url, plus description for live
    # listings via `extra`). A badge without reasons is a bug, so the reasons
    # travel with the score, not just the number.
    listing_text = {
        "title": c.title,
        "org": c.org,
        "pay": c.pay or "",
        "source_url": c.source_url,
        "description": c.extra.get("description", ""),
        "contact": c.extra.get("contact", ""),
        "apply_url": c.extra.get("apply_url", ""),
    }
    result = scam_engine.score(listing_text)
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
        "scam": {
            "score": result.score,
            "band": result.band,
            "reasons": [
                {"rule": r.rule, "weight": r.weight, "quote": r.quote} for r in result.reasons
            ],
        },
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
                "aliases": list(n.aliases),
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


def _live_candidate(record: dict) -> Candidate | None:
    """A live listing that maps to no taxonomy skill can't be scored against
    a held-skills profile, so it's dropped here rather than reaching
    `match()` with an empty `required_skills` (which would look like "fully
    covered" — a false positive, not an honest "no data")."""
    skills = map_text_to_skills(f"{record.get('title', '')} {record.get('description', '')}")
    if not skills:
        return None
    return Candidate(
        id=record["id"],
        title=record.get("title", ""),
        org=record.get("org", ""),
        location=record.get("location", ""),
        required_skills=skills,
        source=record["source"],
        source_url=record["source_url"],
        fetched_at=record["fetched_at"],
        pay=record.get("pay"),
        extra={"is_live": True, "description": record.get("description", "")},
    )


@router.post("/match")
async def match_leads(req: MatchRequest) -> dict:
    _validate(req.held)
    demand = _clean_demand(req.demand)
    telemetry.count(req.persona, "match")

    seed_candidates = list(get_candidates())
    live_candidates: list[Candidate] = []
    live_errors: dict[str, str] = {}

    if req.live:
        remotive_records, remotive_err = await remotive_fetcher.fetch(limit=20)
        adzuna_records, adzuna_err = await adzuna_fetcher.fetch(limit=20)
        if remotive_err:
            live_errors["remotive"] = remotive_err
        if adzuna_err:
            live_errors["adzuna"] = adzuna_err
        for record in remotive_records + adzuna_records:
            candidate = _live_candidate(record)
            if candidate is not None:
                live_candidates.append(candidate)

    candidates = seed_candidates + live_candidates
    results = match(
        get_taxonomy(),
        held=req.held,
        candidates=candidates,
        demand=demand,
        districts=tuple(req.districts),
    )
    by_id = {c.id: c for c in candidates}

    if req.live:
        provenance_note = (
            f"{len(live_candidates)} live listing(s) merged with {len(seed_candidates)} seed listing(s). "
            "Every card keeps its source and fetched_at."
        )
    else:
        provenance_note = (
            "Seed listings, not a live fetch. Every card keeps its source and fetched_at. "
            "Pass live=true to merge in Adzuna / Remotive."
        )

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
        "live": req.live,
        "live_count": len(live_candidates),
        "seed_count": len(seed_candidates),
        "live_errors": live_errors,
        "provenance_note": provenance_note,
        "persona": req.persona,
    }


@router.get("/leads/live")
async def leads_live(q: str = "", limit: int = 10) -> dict:
    """Live job listings (Remotive + Adzuna when its key works), mapped
    through `skills_map` so every card's `required_skills` are taxonomy ids.
    Never crashes when a source is down — that source's error surfaces in
    `errors` instead."""
    remotive_records, remotive_err = await remotive_fetcher.fetch(limit=limit)
    adzuna_records, adzuna_err = await adzuna_fetcher.fetch(q=q, limit=limit)

    records = remotive_records + adzuna_records
    if q:
        needle = q.lower()
        records = [r for r in records if needle in f"{r.get('title', '')} {r.get('description', '')}".lower()]

    cards = []
    for record in records[:limit]:
        candidate = Candidate(
            id=record["id"],
            title=record.get("title", ""),
            org=record.get("org", ""),
            location=record.get("location", ""),
            required_skills=map_text_to_skills(
                f"{record.get('title', '')} {record.get('description', '')}"
            ),
            source=record["source"],
            source_url=record["source_url"],
            fetched_at=record["fetched_at"],
            pay=record.get("pay"),
            extra={"is_live": True, "description": record.get("description", "")},
        )
        # Same shaping + Scam Shield as /match's cards — one card shape, everywhere.
        cards.append(_candidate_json(candidate))

    errors = {k: v for k, v in {"remotive": remotive_err, "adzuna": adzuna_err}.items() if v}
    return {"leads": cards, "count": len(cards), "errors": errors}


@router.get("/schemes")
async def schemes_live(q: str = "", limit: int = 10) -> dict:
    """Live myscheme.gov.in scheme search, stamped with source and fetched_at.
    Never crashes when myscheme is down — its error surfaces in `error`."""
    records, error = await myscheme_fetcher.fetch(q=q, limit=limit)
    return {"schemes": records, "count": len(records), "error": error}


@router.post("/schemes/eligibility")
def scheme_eligibility(req: EligibilityRequest) -> dict:
    """Evaluate reviewed scheme predicates; never let the model decide."""
    telemetry.count(req.persona, "eligibility")
    if req.rules is None:
        return {
            "value": "unknown",
            "reasons": [],
            "matched": [],
            "missing_fields": [],
            "needs_rule_extraction": True,
            "source_url": req.source_url,
            "fetched_at": req.fetched_at,
        }
    try:
        verdict = eligibility_engine.evaluate(req.rules, req.facts)
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(422, f"invalid eligibility rules: {type(exc).__name__}") from exc
    return {
        "value": verdict.value,
        "reasons": list(verdict.reasons),
        "matched": list(verdict.matched),
        "missing_fields": list(verdict.missing_fields),
        "needs_rule_extraction": False,
        "source_url": req.source_url,
        "fetched_at": req.fetched_at,
    }


@router.get("/geocode")
async def geocode(q: str) -> dict:
    """Live Nominatim geocode for one place name. Never crashes when
    Nominatim is down or the place isn't found — `error` surfaces why."""
    records, error = await nominatim_fetcher.fetch(q=q, limit=1)
    if not records:
        return {
            "lat": None,
            "lon": None,
            "display_name": None,
            "source": "nominatim",
            "fetched_at": None,
            "error": error or "not_found",
        }
    return {**records[0], "error": None}


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
        "leads": {
            "count": len(get_candidates()),
            "live": False,
            "note": "GET /leads/live and POST /match(live=true) merge Remotive/Adzuna listings",
        },
    }


# --- assessment (§7.6 Rasch 1PL CAT) ------------------------------------


def _state_to_engine(s: AssessStateModel) -> assess_engine.AssessState:
    if s.se is None:
        return assess_engine.start(theta0=s.theta)
    return assess_engine.AssessState(theta=s.theta, se=s.se, answered=tuple(s.answered))


def _state_to_json(s: assess_engine.AssessState) -> dict:
    return {"theta": round(s.theta, 4), "se": round(s.se, 4), "answered": list(s.answered)}


@router.post("/assess/next")
def assess_next(req: AssessNextRequest) -> dict:
    """The next CAT item at max Fisher information for the current theta, or
    `done: true` once the stopping rule (§7.5) fires. Never returns the
    item's `answer` — that would let the client cheat its own ability
    estimate."""
    state = _state_to_engine(req.state) if req.state else assess_engine.start()
    telemetry.count(req.persona, "assess")

    bank = get_item_bank()
    if req.skill_id is not None:
        bank = tuple(i for i in bank if i.skill_id == req.skill_id)
        if not bank:
            raise HTTPException(404, f"no items for skill_id {req.skill_id!r}")

    if assess_engine.should_stop(state):
        return {"done": True, "state": _state_to_json(state), "item": None}

    exclude = frozenset(item_id for item_id, _ in state.answered)
    item = assess_engine.next_item(state, bank, exclude=exclude)
    if item is None:
        return {"done": True, "state": _state_to_json(state), "item": None}

    return {
        "done": False,
        "state": _state_to_json(state),
        "item": {
            "id": item.id,
            "skill_id": item.skill_id,
            "text": item.text,
            "source": item.source,
        },
    }


@router.post("/assess/answer")
def assess_answer(req: AssessAnswerRequest) -> dict:
    """Grades server-side against the item bank's own answer — the client
    only ever sends what it typed, never a correctness verdict."""
    bank = {i.id: i for i in get_item_bank()}
    item = bank.get(req.item_id)
    if item is None:
        raise HTTPException(404, f"unknown item id: {req.item_id!r}")

    state = _state_to_engine(req.state)
    correct = req.given_answer.strip().casefold() == item.answer.strip().casefold()
    new_state = assess_engine.update(state, item, correct)
    telemetry.count(req.persona, "assess_answer")

    return {
        "correct": correct,
        "state": _state_to_json(new_state),
        "done": assess_engine.should_stop(new_state),
    }


@router.post("/interview/review")
def interview_review(req: InterviewRequest) -> dict:
    """Feedback over the candidate's own words, every item anchored by a quote."""
    try:
        review = interview_engine.review(req.question, req.transcript)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    telemetry.count(req.persona, "interview_review")
    return {
        "feedback": [
            {"area": item.area, "quote": item.quote, "guidance": item.guidance}
            for item in review.feedback
        ],
        "follow_up": review.follow_up,
        "word_count": review.word_count,
        "star": review.star,
        "question_source_url": req.question_source_url,
    }


@router.post("/prep")
def placement_prep(req: PrepRequest) -> dict:
    """Turn a user-confirmed notice date into a deterministic prep calendar."""
    try:
        days = prep_engine.schedule(req.interview_date, datetime.now(UTC).date(), tuple(req.focus))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    telemetry.count(req.persona, "prep")
    return {
        "interview_date": req.interview_date.isoformat(),
        "notice_source_url": req.notice_source_url,
        "days": [{"day": item.day, "focus": item.focus, "hours": item.hours} for item in days],
    }
