"""daari_core.eligibility — deterministic three-valued eligibility (§7.5).

Pure: stdlib only. No I/O, no clock, no randomness (core.md).

safety.md guard 5: `evaluate()` returns `True | False | Unknown` with reasons
and `missing_fields`. **`Unknown` never renders as "qualifies".** Every leaf
predicate stores the snippet that justifies it — extracted by the LLM at
temperature 0 (apps/api's `extract_rules.py`), decided here.

AST node shapes:
    {"op": "and" | "or", "children": [...]}
    {"op": "not", "child": {...}}
    leaf: {"op": "lte"|"gte"|"eq"|"in"|"exists", "field": str, "value": Any, "snippet": str}

Kleene three-valued logic: and(false, unknown)=false, and(true, unknown)=unknown,
or(true, unknown)=true, or(false, unknown)=unknown, not(unknown)=unknown. A leaf
whose field is absent from `facts` (or is None) is unknown, and the field name
lands in `missing_fields` — never dropped, never silently treated as false.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

Value = Literal["true", "false", "unknown"]

_LEAF_OPS = {"lte", "gte", "eq", "in", "exists"}


@dataclass(frozen=True)
class Verdict:
    value: Value
    reasons: tuple[str, ...]
    missing_fields: tuple[str, ...]
    matched: tuple[str, ...]


def _and(a: Value, b: Value) -> Value:
    if a == "false" or b == "false":
        return "false"
    if a == "unknown" or b == "unknown":
        return "unknown"
    return "true"


def _or(a: Value, b: Value) -> Value:
    if a == "true" or b == "true":
        return "true"
    if a == "unknown" or b == "unknown":
        return "unknown"
    return "false"


def _not(a: Value) -> Value:
    return {"true": "false", "false": "true", "unknown": "unknown"}[a]


def evaluate(ast: Mapping[str, Any], facts: Mapping[str, Any]) -> Verdict:
    """Decide `ast` against `facts`. Idempotent: identical args, identical Verdict."""
    missing: set[str] = set()
    reasons: list[str] = []
    matched: list[str] = []

    def eval_node(node: Mapping[str, Any]) -> Value:
        op = node.get("op")
        if op == "and":
            result: Value = "true"
            for child in node["children"]:
                result = _and(result, eval_node(child))
            return result
        if op == "or":
            result = "false"
            for child in node["children"]:
                result = _or(result, eval_node(child))
            return result
        if op == "not":
            return _not(eval_node(node["child"]))
        if op in _LEAF_OPS:
            return eval_leaf(node, op)
        raise ValueError(f"unknown op: {op!r}")

    def eval_leaf(node: Mapping[str, Any], op: str) -> Value:
        if "snippet" not in node:
            raise ValueError(f"leaf predicate missing 'snippet': {node!r}")
        field = node["field"]
        snippet = node["snippet"]
        if field not in facts or facts[field] is None:
            missing.add(field)
            return "unknown"

        actual = facts[field]
        target = node.get("value")
        if op == "exists":
            outcome = True
        elif op == "lte":
            outcome = actual <= target
        elif op == "gte":
            outcome = actual >= target
        elif op == "eq":
            outcome = actual == target
        else:  # "in"
            outcome = actual in target

        reasons.append(snippet)
        if outcome:
            matched.append(snippet)
        return "true" if outcome else "false"

    value = eval_node(ast)
    return Verdict(
        value=value,
        reasons=tuple(reasons),
        missing_fields=tuple(sorted(missing)),
        matched=tuple(matched),
    )
