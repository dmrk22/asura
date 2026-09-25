"""daari.items_loader — optional CAT item bank, loaded from committed data.

Like `taxonomy_loader` and `leads`, all I/O lives here; `daari_core.assess`
never touches YAML or the network (core.md).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from daari_core.assess import Item

REPO_ROOT = Path(__file__).resolve().parents[3]
ITEMS_FILE = REPO_ROOT / "data" / "items" / "items.yaml"


@lru_cache(maxsize=1)
def get_item_bank() -> tuple[Item, ...]:
    if not ITEMS_FILE.exists():
        return ()
    with ITEMS_FILE.open("r", encoding="utf-8") as f:
        rows = yaml.safe_load(f)
    if not rows:
        return ()
    items = tuple(
        Item(
            id=row["id"],
            skill_id=row["skill_id"],
            band=float(row["band"]),
            text=row["text"],
            answer=row["answer"],
            # Every row carries either a `source` citation or a stated
            # `rationale` (data.md: "a node without a source is not a
            # node" — the two_wheeler_* items use rationale instead).
            source=row.get("source", row.get("rationale", "")),
            rationale=row.get("rationale", ""),
        )
        for row in rows
    )
    ids = [i.id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("item bank has duplicate ids")
    return items
