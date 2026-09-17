"""One engine, provably. apps/api/daari/personas/*.py must never define
matching, roadmap, eligibility, assessment, scam or scheduling logic
locally, and must never do arithmetic on a score-shaped value — that
logic lives in daari_core and nowhere else (CLAUDE.md non-negotiable #1).

The persona directory doesn't exist yet in the P1 skeleton (routes land
later); we skip with a clear reason rather than silently passing on a
typo'd path. `test_fixture_violating_persona_is_detected` proves the scan
itself works, against a fixture built to violate the rule.
"""

import ast
from pathlib import Path

import pytest

ENGINE_NAMES = {"match", "roadmap", "eligibility", "assess", "scam", "schedule"}

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent.parent.parent
PERSONAS_DIR = REPO_ROOT / "apps" / "api" / "daari" / "personas"
FIXTURE_DIR = TESTS_DIR / "fixtures" / "violating_persona"


def _defines_engine_logic(tree: ast.Module) -> list[str]:
    """A def/class named like an engine entry point, defined (not imported)."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in ENGINE_NAMES:
            violations.append(f"defines `{node.name}` locally (import it from daari_core instead)")
    return violations


def _looks_like_score(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return "score" in node.id.lower()
    if isinstance(node, ast.Attribute):
        return "score" in node.attr.lower()
    return False


def _does_score_arithmetic(tree: ast.Module) -> list[str]:
    """A BinOp where either operand looks like a score — that's engine work."""
    violations = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div))
            and (_looks_like_score(node.left) or _looks_like_score(node.right))
        ):
            violations.append(f"line {node.lineno}: arithmetic on a score-shaped value")
    return violations


def _scan_dir(dir_path: Path) -> dict[str, list[str]]:
    violations: dict[str, list[str]] = {}
    for path in sorted(dir_path.glob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        hits = _defines_engine_logic(tree) + _does_score_arithmetic(tree)
        if hits:
            violations[path.name] = hits
    return violations


def test_personas_directory_or_skip_with_reason():
    if not PERSONAS_DIR.exists():
        pytest.skip(
            f"{PERSONAS_DIR} does not exist yet (P1 skeleton — persona routes land in a later "
            "phase); skipping with a reason, not passing silently on a missing/typo'd path."
        )
    violations = _scan_dir(PERSONAS_DIR)
    assert not violations, f"engine logic leaked into persona adapters: {violations}"


def test_fixture_violating_persona_is_detected():
    assert FIXTURE_DIR.exists(), f"missing fixture dir {FIXTURE_DIR}"
    violations = _scan_dir(FIXTURE_DIR)
    assert violations, "fixture is supposed to violate the shared-engine rule but nothing was detected"
    assert "bad_persona.py" in violations
