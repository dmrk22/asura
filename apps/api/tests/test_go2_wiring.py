"""Regression tests for the GO 2 join: scam scoring on every /match card,
and the /assess routes over the real item bank.

Written because these are exactly the two things GO 2 wired that had no test
of their own yet — `_candidate_json` gaining a `scam` field, and the new
stateless CAT routes. `test_routes.py` covers everything from GO 1.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from daari.main import app

RAVI = {"spoken_english": 2, "basic_numeracy": 2, "digital_literacy": 1}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# --- scam score on every match card -------------------------------------


def test_match_cards_all_carry_a_scam_verdict_with_reasons_or_empty(client: TestClient):
    r = client.post("/match", json={"held": RAVI})
    assert r.status_code == 200
    matches = r.json()["matches"]
    assert matches, "seed data must produce at least one match"
    for card in matches:
        assert "scam" in card
        assert card["scam"]["band"] in {"clear", "check", "red"}
        assert 0.0 <= card["scam"]["score"] <= 1.0
        # A badge without reasons is a bug (safety.md guard 3): if the band
        # is not clear, there must be at least one quoted reason.
        if card["scam"]["band"] != "clear":
            assert card["scam"]["reasons"], card
            for reason in card["scam"]["reasons"]:
                assert reason["quote"]


def test_a_clean_seed_listing_scores_clear_with_no_reasons(client: TestClient):
    r = client.post("/match", json={"held": RAVI})
    body = r.json()
    # Seed listings carry no scam-triggering text — every one should be clear.
    for card in body["matches"]:
        if card["source"] == "seed":
            assert card["scam"]["band"] == "clear"
            assert card["scam"]["reasons"] == []


# --- /assess: stateless Rasch 1PL CAT over the real item bank -----------


def test_assess_next_returns_an_item_without_leaking_the_answer(client: TestClient):
    r = client.post("/assess/next", json={"skill_id": "sql_querying"})
    assert r.status_code == 200
    body = r.json()
    assert body["done"] is False
    assert body["item"]["skill_id"] == "sql_querying"
    assert "answer" not in body["item"]


def test_assess_answer_grades_server_side_and_updates_theta(client: TestClient):
    r1 = client.post("/assess/next", json={"skill_id": "sql_querying"})
    item = r1.json()["item"]
    state = r1.json()["state"]

    r2 = client.post(
        "/assess/answer",
        json={"state": state, "item_id": item["id"], "given_answer": "definitely not the answer"},
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["correct"] is False
    assert body["state"]["se"] <= state["se"]  # SE never increases


def test_assess_stops_within_six_items(client: TestClient):
    state = None
    for _ in range(6):
        r = client.post("/assess/next", json={"state": state, "skill_id": "sql_querying"})
        body = r.json()
        if body["done"]:
            break
        item = body["item"]
        r2 = client.post(
            "/assess/answer",
            json={"state": body["state"], "item_id": item["id"], "given_answer": "x"},
        )
        state = r2.json()["state"]
    # By item 6 the stopping rule must have fired (should_stop is a hard cap).
    final = client.post("/assess/next", json={"state": state, "skill_id": "sql_querying"})
    assert final.json()["done"] is True


def test_assess_answer_rejects_an_unknown_item_id(client: TestClient):
    r = client.post(
        "/assess/answer",
        json={"state": {"theta": 0.0, "se": None, "answered": []}, "item_id": "nope", "given_answer": "x"},
    )
    assert r.status_code == 404
