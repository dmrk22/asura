"""Engine route tests.

These hit the real app with the real committed taxonomy — no mocked engine.
They do not need Postgres or Redis: only `/health` touches those, and these
routes are pure engine calls over committed data.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from daari.main import app

BASELINE_SKILLS = {
    "spoken_english": 3,
    "basic_numeracy": 3,
    "digital_literacy": 3,
    "python_programming": 2,
    "sql_querying": 2,
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# --- taxonomy / empty profile store -------------------------------------


def test_taxonomy_returns_the_real_seed(client: TestClient):
    r = client.get("/taxonomy")
    assert r.status_code == 200
    body = r.json()
    assert body["counts"]["skills"] == 24
    assert body["counts"]["roles"] == 11
    assert {role["id"] for role in body["roles"]} == {
        "customer_support_executive",
        "data_analyst",
        "data_entry_operator",
        "data_operations_associate",
        "delivery_executive",
        "delivery_operations_coordinator",
        "digital_services_assistant",
        "ecommerce_delivery_associate",
        "field_sales_executive",
        "retail_sales_associate",
        "warehouse_packing_associate",
    }


def test_every_skill_ships_a_source_and_a_telugu_label(client: TestClient):
    for skill in client.get("/taxonomy").json()["skills"]:
        assert skill["source"], f"{skill['id']} has no source"
        assert skill["label_te"], f"{skill['id']} has no Telugu label"
        assert isinstance(skill["aliases"], list), f"{skill['id']} has no aliases list"


def test_personas_starts_empty(client: TestClient):
    body = client.get("/personas").json()
    assert body == {"personas": []}


# --- roadmap ------------------------------------------------------------


def test_roadmap_for_a_blank_profile(client: TestClient):
    r = client.post("/roadmap", json={"held": {}, "goal": "data_analyst"})
    assert r.status_code == 200
    path = r.json()["path"]
    assert path["steps"], "a blank profile must get a real path"
    assert path["total_hours"] > 0
    assert all(step["why"] for step in path["steps"])
    assert all(step["source"] for step in path["steps"])


def test_roadmap_rejects_an_unknown_goal(client: TestClient):
    r = client.post("/roadmap", json={"held": {}, "goal": "astronaut"})
    assert r.status_code == 404


def test_roadmap_rejects_an_unknown_skill(client: TestClient):
    r = client.post("/roadmap", json={"held": {"telekinesis": 3}, "goal": "data_analyst"})
    assert r.status_code == 422


def test_roadmap_rejects_an_out_of_range_level(client: TestClient):
    r = client.post("/roadmap", json={"held": {"sql_querying": 9}, "goal": "data_analyst"})
    assert r.status_code == 422


def test_held_skills_shorten_a_path(client: TestClient):
    blank = client.post("/roadmap", json={"held": {}, "goal": "data_analyst"}).json()["path"]
    baseline = client.post("/roadmap", json={"held": BASELINE_SKILLS, "goal": "data_analyst"}).json()["path"]
    assert baseline["total_hours"] < blank["total_hours"]


# --- learn (the Before | After beat) ------------------------------------


def test_learning_sql_shortens_the_path_and_reports_a_learner_diff(client: TestClient):
    r = client.post(
        "/roadmap/learn",
        json={"held": BASELINE_SKILLS, "goal": "data_analyst", "skill": "sql_querying", "level": 5},
    )
    assert r.status_code == 200
    body = r.json()

    assert "sql_querying" in body["diff"]["removed"]
    assert body["diff"]["cause"] == "learner"
    assert body["diff"]["hours_delta"] < 0
    assert body["after"]["total_hours"] < body["before"]["total_hours"]
    assert body["held_after"]["sql_querying"] == 5


def test_learning_never_lengthens_the_path(client: TestClient):
    """The §7.3 invariant, enforced at the HTTP boundary too."""
    for skill in ("sql_querying", "python_programming", "ms_excel_basic", "statistics_fundamentals"):
        body = client.post(
            "/roadmap/learn",
            json={"held": {}, "goal": "data_analyst", "skill": skill, "level": 5},
        ).json()
        assert len(body["after"]["steps"]) <= len(body["before"]["steps"]), skill
        assert body["diff"]["hours_delta"] <= 0, skill


def test_relearning_a_held_skill_is_an_empty_diff(client: TestClient):
    body = client.post(
        "/roadmap/learn",
        json={"held": {"sql_querying": 5}, "goal": "data_analyst", "skill": "sql_querying", "level": 5},
    ).json()
    assert body["diff"]["empty"] is True
    assert body["diff"]["cause"] == "none"


# --- market shock -------------------------------------------------------


def test_market_shock_reorders_and_reports_a_market_cause(client: TestClient):
    r = client.post(
        "/roadmap/shock",
        json={"held": {}, "goal": "data_analyst", "skill": "python_programming", "weight": 2.0},
    )
    assert r.status_code == 200
    body = r.json()

    assert body["diff"]["cause"] == "market"
    assert body["diff"]["reordered"], "a 2x shock on the longest skill must reorder"
    assert body["diff"]["removed"] == [] and body["diff"]["added"] == []
    assert body["diff"]["hours_delta"] == 0


def test_market_shock_reports_the_clamped_weight_not_the_requested_one(client: TestClient):
    """An honest number: asking for 50x must not claim 50x was applied."""
    body = client.post(
        "/roadmap/shock",
        json={"held": {}, "goal": "data_analyst", "skill": "python_programming", "weight": 50.0},
    ).json()
    assert body["requested_weight"] == 50.0
    assert body["applied_weight"] == 2.0


def test_shock_cannot_put_a_skill_before_its_prerequisites(client: TestClient):
    body = client.post(
        "/roadmap/shock",
        json={"held": {}, "goal": "data_analyst", "skill": "data_visualization_powerbi", "weight": 2.0},
    ).json()
    order = [s["skill"] for s in body["after"]["steps"]]
    assert order.index("data_cleaning") < order.index("data_visualization_powerbi")
    assert order.index("sql_querying") < order.index("data_cleaning")


# --- match --------------------------------------------------------------


def test_match_starts_with_no_locally_saved_leads(client: TestClient):
    r = client.post("/match", json={"held": BASELINE_SKILLS, "districts": ["Vijayawada"]})
    assert r.status_code == 200
    body = r.json()
    assert body["matches"] == []
    assert body["count"] == 0
    assert body["saved_count"] == 0


def test_empty_match_response_explains_how_to_search_live_leads(client: TestClient):
    body = client.post("/match", json={"held": BASELINE_SKILLS}).json()
    assert body["live"] is False
    assert "0 locally saved listing(s)" in body["provenance_note"]


# --- evidence -----------------------------------------------------------


def test_evidence_counters_move_for_both_personas(client: TestClient):
    client.post("/roadmap", json={"held": {}, "goal": "data_analyst", "persona": "student"})
    client.post("/roadmap", json={"held": {}, "goal": "delivery_executive", "persona": "rural"})

    body = client.get("/evidence").json()
    calls = body["shared_engine"]["calls_by_persona"]
    assert calls.get("student", {}).get("roadmap", 0) > 0
    assert calls.get("rural", {}).get("roadmap", 0) > 0
    assert body["shared_engine"]["package"] == "daari_core"
    assert body["leads"]["live"] is False
    assert body["leads"]["count"] == 0


def test_eligibility_without_reviewed_rules_is_honest_unknown(client: TestClient):
    body = client.post(
        "/schemes/eligibility",
        json={"source_url": "https://example.test/scheme", "fetched_at": "2026-09-20T00:00:00Z"},
    ).json()
    assert body["value"] == "unknown"
    assert body["needs_rule_extraction"] is True


def test_interview_feedback_is_anchored_to_the_transcript(client: TestClient):
    transcript = "I built a dashboard for my class project."
    body = client.post(
        "/interview/review",
        json={
            "question": "Tell me about a project.",
            "transcript": transcript,
            "question_source_url": "https://example.test/question",
        },
    ).json()
    assert body["feedback"]
    assert all(item["quote"] in transcript for item in body["feedback"])


def test_prep_makes_a_plan_from_a_confirmed_date(client: TestClient):
    body = client.post(
        "/prep",
        json={
            "interview_date": "2026-12-01",
            "focus": ["SQL", "mock interview"],
            "notice_source_url": "https://example.test/notice",
        },
    ).json()
    assert body["days"]
    assert body["notice_source_url"] == "https://example.test/notice"
