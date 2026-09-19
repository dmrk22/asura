"""daari.skills_map — deterministic free-text -> taxonomy skill-id mapping.

No LLM call happens here (nothing to mock): this is pure regex matching
against the real committed `data/taxonomy/skills.yaml` aliases.
"""

from __future__ import annotations

from daari.skills_map import DEFAULT_REQUIRED_LEVEL, map_text_to_skills


def test_maps_a_known_alias_to_its_skill_id():
    result = map_text_to_skills("We need someone strong in SQL and Python.")

    assert result["sql_querying"] == DEFAULT_REQUIRED_LEVEL
    assert result["python_programming"] == DEFAULT_REQUIRED_LEVEL


def test_is_case_insensitive():
    result = map_text_to_skills("comfortable with python and sql")

    assert "python_programming" in result
    assert "sql_querying" in result


def test_word_boundary_does_not_match_inside_another_word():
    # "sql" must not match "postgresql" (data.md / api.md: deterministic,
    # not a substring free-for-all).
    result = map_text_to_skills("Experience with PostgreSQL databases.")

    assert "sql_querying" not in result


def test_no_match_returns_empty_dict():
    assert map_text_to_skills("Deliver packages around town on a bicycle.") == {}


def test_longest_alias_wins_on_an_overlapping_span():
    # "spreadsheets" (ms_excel_basic) is a substring of "advanced
    # spreadsheets" (excel_advanced) — the longer, more specific alias
    # claims that span; the shorter one must not also fire for it.
    result = map_text_to_skills("Must be comfortable with advanced spreadsheets.")

    assert "excel_advanced" in result
    assert "ms_excel_basic" not in result


def test_a_standalone_shorter_alias_still_matches_elsewhere():
    # The same shorter alias, when it appears on its own (no overlapping
    # longer alias claiming its span), still matches normally.
    result = map_text_to_skills("Please bring your own spreadsheets.")

    assert "ms_excel_basic" in result
