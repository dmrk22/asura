"""The one real engine: roadmap, before/after diff, job matching.

Pure functions over the hardcoded graph in data.py — no I/O, no network,
no randomness. Both API routes call these; nothing duplicates this logic.
"""

from __future__ import annotations

from app.data import SKILLS


def _closure(goal: str, skills: dict) -> set[str]:
    """All skills reachable by walking `requires` edges from goal, goal included."""
    seen: set[str] = set()
    stack = [goal]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(skills[node]["requires"])
    return seen


def compute_roadmap(held: list[str], goal: str, skills: dict = SKILLS) -> dict:
    if goal not in skills:
        raise ValueError(f"unknown goal skill: {goal!r}")
    held_set = set(held)
    missing = _closure(goal, skills) - held_set

    # Kahn's algorithm over the subgraph induced by `missing`, so an already-held
    # skill can't block ordering. Ties broken by hours then id — deterministic.
    remaining_deps = {n: {r for r in skills[n]["requires"] if r in missing} for n in missing}
    ordered: list[str] = []
    while remaining_deps:
        ready = sorted(
            (n for n, deps in remaining_deps.items() if not deps),
            key=lambda n: (skills[n]["hours"], n),
        )
        if not ready:
            raise RuntimeError("cycle detected in skill graph — data.py is not a DAG")
        for n in ready:
            del remaining_deps[n]
        for deps in remaining_deps.values():
            deps.difference_update(ready)
        ordered.extend(ready)

    steps = [
        {"skill": n, "hours": skills[n]["hours"], "requires": skills[n]["requires"]}
        for n in ordered
    ]
    return {"goal": goal, "steps": steps, "total_hours": sum(s["hours"] for s in steps)}


def diff_roadmap(held: list[str], goal: str, new_skill: str, skills: dict = SKILLS) -> dict:
    if new_skill not in skills:
        raise ValueError(f"unknown skill: {new_skill!r}")

    before = compute_roadmap(held, goal, skills)
    after_held = list(held) if new_skill in held else [*held, new_skill]
    after = compute_roadmap(after_held, goal, skills)

    before_ids = [s["skill"] for s in before["steps"]]
    after_ids = [s["skill"] for s in after["steps"]]
    after_pos = {sid: i for i, sid in enumerate(after_ids)}
    before_pos = {sid: i for i, sid in enumerate(before_ids)}

    removed = [sid for sid in before_ids if sid not in after_pos]
    added = [sid for sid in after_ids if sid not in before_pos]

    # "Reordered" = relative order among skills present both before and after
    # actually changed — not just index-shifted because earlier steps were removed.
    common_before_order = [sid for sid in before_ids if sid in after_pos]
    common_after_order = sorted(common_before_order, key=lambda sid: after_pos[sid])
    before_rank = {sid: i for i, sid in enumerate(common_before_order)}
    after_rank = {sid: i for i, sid in enumerate(common_after_order)}
    reordered = [sid for sid in common_before_order if before_rank[sid] != after_rank[sid]]

    return {
        "before": before,
        "after": after,
        "removed": removed,
        "added": added,
        "reordered": reordered,
        "hours_saved": before["total_hours"] - after["total_hours"],
    }


def match_jobs(held: list[str], jobs: list[dict], fetched_at: str) -> list[dict]:
    held_set = set(held)
    results = []
    for job in jobs:
        required = job["required_skills"]
        matched = [s for s in required if s in held_set]
        missing = [s for s in required if s not in held_set]
        score = len(matched) / len(required) if required else 0.0
        results.append(
            {
                **job,
                "match_score": round(score, 3),
                "matched_skills": matched,
                "missing_skills": missing,
                "fetched_at": fetched_at,
            }
        )
    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results
