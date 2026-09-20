"""daari_core — the shared engine. Both persona routes import this; nothing else may hold this logic.

Pure: numpy, networkx and the stdlib only. No FastAPI, SQLAlchemy, httpx, redis or LLM client.
Deterministic: no clock reads, no randomness, no network, no I/O in match/roadmap/eligibility/
assess/scam/interview_metrics. Engine modules (match.py, roadmap.py, ...) arrive in P2, with tests.
"""

__version__ = "0.1.0"
from . import (
    assess,
    eligibility,
    geo,
    graph,
    interview,
    match,
    prep,
    profile,
    roadmap,
    scam,
    taxonomy,
    telemetry,
)

__all__ = [
    "assess", "eligibility", "geo", "graph", "interview", "match", "prep", "profile", "roadmap", "scam", "taxonomy", "telemetry"
]
