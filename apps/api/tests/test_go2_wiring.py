"""Regression coverage for empty leads and the stateless CAT routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from daari.main import app

BASELINE_SKILLS = {"spoken_english": 2, "basic_numeracy": 2, "digital_literacy": 1}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# --- scam score on every match card -------------------------------------


def test_match_starts_empty_without_saved_listings(client: TestClient):
    r = client.post("/match", json={"held": BASELINE_SKILLS})
    assert r.status_code == 200
    matches = r.json()["matches"]
    assert matches == []


# --- /assess: an empty bank is an honest empty state --------------------


def test_assess_next_reports_no_questions_when_the_bank_is_empty(client: TestClient):
    r = client.post("/assess/next", json={"skill_id": "sql_querying"})
    assert r.status_code == 200
    body = r.json()
    assert body["done"] is True
    assert body["available"] is False
    assert body["item"] is None


def test_assess_answer_rejects_an_unknown_item_id(client: TestClient):
    r = client.post(
        "/assess/answer",
        json={"state": {"theta": 0.0, "se": None, "answered": []}, "item_id": "nope", "given_answer": "x"},
    )
    assert r.status_code == 404
