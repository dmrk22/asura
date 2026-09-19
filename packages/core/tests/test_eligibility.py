"""Eligibility tests (§7.5, safety.md guard 5): three-valued Kleene logic.

`unknown` never collapses to `qualifies` — that regression is asserted
explicitly, not just implied by the truth table.
"""

from __future__ import annotations

import pytest

from daari_core.eligibility import evaluate


def leaf(op, field, value=None, snippet="because"):
    return {"op": op, "field": field, "value": value, "snippet": snippet}


# --- Kleene truth table, exhaustively ----------------------------------

TRUE_LEAF = leaf("gte", "age", 18, "age >= 18")
FALSE_LEAF = leaf("lte", "age", 10, "age <= 10")
UNKNOWN_LEAF = leaf("gte", "income", 0, "income known")

VALUES = {
    "true": {"age": 18},
    "false": {"age": 18},
    "unknown": {},
}


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("true", "true", "true"),
        ("true", "false", "false"),
        ("true", "unknown", "unknown"),
        ("false", "true", "false"),
        ("false", "false", "false"),
        ("false", "unknown", "false"),
        ("unknown", "true", "unknown"),
        ("unknown", "false", "false"),
        ("unknown", "unknown", "unknown"),
    ],
)
def test_and_truth_table(a, b, expected):
    leaves = {"true": TRUE_LEAF, "false": FALSE_LEAF, "unknown": UNKNOWN_LEAF}
    facts = {**VALUES[a], **VALUES[b]}
    ast = {"op": "and", "children": [leaves[a], leaves[b]]}
    assert evaluate(ast, facts).value == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("true", "true", "true"),
        ("true", "false", "true"),
        ("true", "unknown", "true"),
        ("false", "true", "true"),
        ("false", "false", "false"),
        ("false", "unknown", "unknown"),
        ("unknown", "true", "true"),
        ("unknown", "false", "unknown"),
        ("unknown", "unknown", "unknown"),
    ],
)
def test_or_truth_table(a, b, expected):
    leaves = {"true": TRUE_LEAF, "false": FALSE_LEAF, "unknown": UNKNOWN_LEAF}
    facts = {**VALUES[a], **VALUES[b]}
    ast = {"op": "or", "children": [leaves[a], leaves[b]]}
    assert evaluate(ast, facts).value == expected


@pytest.mark.parametrize(
    "leaf_name,expected",
    [("true", "false"), ("false", "true"), ("unknown", "unknown")],
)
def test_not_truth_table(leaf_name, expected):
    leaves = {"true": TRUE_LEAF, "false": FALSE_LEAF, "unknown": UNKNOWN_LEAF}
    ast = {"op": "not", "child": leaves[leaf_name]}
    assert evaluate(ast, VALUES[leaf_name]).value == expected


# --- regression: unknown never collapses to qualifies ------------------


def test_unknown_never_reads_as_qualifies():
    ast = {"op": "and", "children": [TRUE_LEAF, UNKNOWN_LEAF]}
    verdict = evaluate(ast, {"age": 18})
    assert verdict.value == "unknown"
    assert verdict.value != "true"
    assert "income" in verdict.missing_fields


def test_missing_field_because_value_is_none_also_unknown():
    ast = leaf("eq", "district", "Guntur")
    verdict = evaluate(ast, {"district": None})
    assert verdict.value == "unknown"
    assert verdict.missing_fields == ("district",)


# --- shape ---------------------------------------------------------------


def test_missing_fields_sorted_and_deduped():
    ast = {
        "op": "and",
        "children": [leaf("exists", "b_field"), leaf("exists", "a_field"), leaf("exists", "a_field")],
    }
    verdict = evaluate(ast, {})
    assert verdict.missing_fields == ("a_field", "b_field")


def test_nested_tree():
    ast = {
        "op": "and",
        "children": [
            leaf("gte", "age", 18, "age >= 18"),
            {
                "op": "or",
                "children": [
                    leaf("eq", "district", "Guntur", "lives in Guntur"),
                    leaf("in", "district", ("Guntur", "Vijayawada"), "or a neighbouring district"),
                ],
            },
            {"op": "not", "child": leaf("eq", "has_criminal_record", True, "no record")},
        ],
    }
    facts = {"age": 20, "district": "Guntur", "has_criminal_record": False}
    verdict = evaluate(ast, facts)
    assert verdict.value == "true"
    assert "age >= 18" in verdict.matched
    # The "no record" leaf itself evaluates false (has_criminal_record is
    # False, not True) and only reads true after `not` negates it — `matched`
    # tracks each leaf's own raw outcome, not the tree's post-negation value.
    assert "no record" not in verdict.matched
    assert "no record" in verdict.reasons


def test_idempotent():
    ast = {"op": "and", "children": [TRUE_LEAF, UNKNOWN_LEAF]}
    facts = {"age": 18}
    v1 = evaluate(ast, facts)
    v2 = evaluate(ast, facts)
    assert v1 == v2


def test_unknown_op_raises():
    with pytest.raises(ValueError):
        evaluate({"op": "xor", "children": []}, {})


def test_leaf_without_snippet_raises():
    with pytest.raises(ValueError):
        evaluate({"op": "gte", "field": "age", "value": 18}, {"age": 20})


def test_exists_op():
    ast = leaf("exists", "aadhaar", snippet="has aadhaar")
    assert evaluate(ast, {"aadhaar": "1234"}).value == "true"
    assert evaluate(ast, {}).value == "unknown"
    assert evaluate(ast, {"aadhaar": None}).value == "unknown"
