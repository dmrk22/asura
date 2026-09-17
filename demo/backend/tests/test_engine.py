"""One sanity check: the roadmap shrinks when you learn a required skill, for real."""

from app.data import PROFILES, SKILLS
from app.engine import diff_roadmap


def test_learning_a_required_skill_actually_shrinks_the_roadmap():
    priya = PROFILES["priya"]
    result = diff_roadmap(priya["held"], priya["goal"], "statistics_fundamentals")

    before_ids = {s["skill"] for s in result["before"]["steps"]}
    after_ids = {s["skill"] for s in result["after"]["steps"]}
    hours = SKILLS["statistics_fundamentals"]["hours"]

    assert "statistics_fundamentals" in before_ids
    assert "statistics_fundamentals" not in after_ids
    assert result["removed"] == ["statistics_fundamentals"]
    assert result["hours_saved"] == hours
    assert result["after"]["total_hours"] == result["before"]["total_hours"] - hours
