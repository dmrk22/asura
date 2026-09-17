"""daari_core is pure: numpy, networkx and the stdlib only.

Walks the real file tree under daari_core/ with `ast` and fails if any file
imports a module that would break purity (a web framework, a DB driver, an
HTTP client, or an LLM SDK). This is a real assertion over the real files,
not a hardcoded list of what's already imported.
"""

import ast
from pathlib import Path

FORBIDDEN = {
    "fastapi",
    "sqlalchemy",
    "httpx",
    "redis",
    "asyncpg",
    "alembic",
    "openai",
    "groq",
    "google",
    "anthropic",
    "ollama",
}

CORE_DIR = Path(__file__).resolve().parent.parent / "daari_core"


def _imported_top_level_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def test_no_forbidden_imports_anywhere_under_daari_core():
    py_files = sorted(CORE_DIR.rglob("*.py"))
    assert py_files, f"expected at least one .py file under {CORE_DIR}"

    violations: dict[str, list[str]] = {}
    for path in py_files:
        hit = _imported_top_level_names(path) & FORBIDDEN
        if hit:
            violations[str(path.relative_to(CORE_DIR))] = sorted(hit)

    assert not violations, f"forbidden imports found in daari_core: {violations}"
