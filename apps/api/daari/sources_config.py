"""daari.sources_config — reads `data/sources.yaml`, the only file allowed to
name a live source (CLAUDE.md non-negotiable 2, data.md). Fetchers that need
source-specific, non-secret config (e.g. myscheme's public browser API key)
read it from here rather than hardcoding a second copy of it.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCES_FILE = REPO_ROOT / "data" / "sources.yaml"


@lru_cache(maxsize=1)
def get_sources() -> dict[str, dict]:
    entries = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or []
    return {e["id"]: e for e in entries}
