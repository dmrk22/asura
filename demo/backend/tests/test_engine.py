"""One sanity check: the roadmap shrinks when you learn a required skill, for real."""

from app.data import PROFILES
from app.engine import diff_roadmap


def test_learning_a_required_skill_actually_shrinks_the_roadmap():
    priya = PROFILES["priya"]
    result = diff_roadmap(priya["held"], priya["goal"], "statistics")

    before_ids = {s["skill"] for s in result["before"]["steps"]}
    after_ids = {s["skill"] for s in result["after"]["steps"]}

    assert "statistics" in before_ids
    assert "statistics" not in after_ids
    assert result["removed"] == ["statistics"]
    assert result["hours_saved"] == 20
    assert result["after"]["total_hours"] == result["before"]["total_hours"] - 20
