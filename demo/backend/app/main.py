"""DAARI localhost demo API. No Docker, no Postgres, no Redis, no network calls.

Run: uv run uvicorn app.main:app --port 8000 --reload   (from demo/backend/)
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.data import JOBS, PROFILES, SKILLS
from app.engine import compute_roadmap, diff_roadmap, match_jobs

# Stamped once at process start — every job in this demo shares one "fetched at"
# instant rather than each re-reading the clock (there's only one seed load here).
SEED_FETCHED_AT = datetime.now(timezone.utc).isoformat()

app = FastAPI(title="DAARI demo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RoadmapRequest(BaseModel):
    profile: list[str]
    goal: str


class LearnRequest(BaseModel):
    profile: list[str]
    goal: str
    new_skill: str


@app.get("/health")
def health() -> dict:
    return {"ok": True, "skills": len(SKILLS), "jobs": len(JOBS)}


@app.get("/profiles")
def profiles() -> dict:
    return PROFILES


@app.post("/roadmap")
def roadmap(req: RoadmapRequest) -> dict:
    try:
        return compute_roadmap(req.profile, req.goal)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/roadmap/learn")
def roadmap_learn(req: LearnRequest) -> dict:
    try:
        return diff_roadmap(req.profile, req.goal, req.new_skill)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/jobs")
def jobs(skills: str = "") -> list[dict]:
    held = [s.strip() for s in skills.split(",") if s.strip()]
    return match_jobs(held, JOBS, SEED_FETCHED_AT)
