"""The one real engine: roadmap, before/after diff, job matching.

Pure functions over the real taxonomy loaded in data.py — no I/O, no network,
no randomness. Both API routes call these; nothing duplicates this logic.

A "goal" here is a role (data_analyst / delivery_executive), i.e. a set of
required skills — matching DAARI_BUILD_PLAN.md §7.1's role schema, not a
single invented capstone skill.
"""

from __future__ import annotations

from app.data import ROLES, SKILLS


def _closure(required: list[str], skills: dict) -> set[str]:
    """All skills reachable by walking `requires` edges from the required
    set, required skills included."""
    seen: set[str] = set()
    stack = list(required)
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(skills[node]["requires"])
    return seen


def _why(n: str, closure: set[str], direct_required: set[str], skills: dict, role_label: str) -> list[str]:
    """A real, computed reason — not invented copy. Either the role names this
    skill directly, or some other skill in the same closure needs it."""
    reasons = []
    if n in direct_required:
        reasons.append(f"Required for {role_label}")
    dependents = sorted(
        m for m in closure if m != n and n in skills[m]["requires"]
    )
    for m in dependents[:2]:
        reasons.append(f"Needed for {skills[m]['label_en']}")
    if not reasons:
        reasons.append(f"On the path to {role_label}")
    return reasons


def compute_roadmap(held: list[str], goal: str, skills: dict = SKILLS, roles: dict = ROLES) -> dict:
    if goal not in roles:
        raise ValueError(f"unknown goal role: {goal!r}")
    role = roles[goal]
    held_set = set(held)
    direct_required = set(role["required_skills"])
    closure = _closure(role["required_skills"], skills)
    missing = closure - held_set

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
            raise RuntimeError("cycle detected in skill graph — data/taxonomy is not a DAG")
        for n in ready:
            del remaining_deps[n]
        for deps in remaining_deps.values():
            deps.difference_update(ready)
        ordered.extend(ready)

    steps = [
        {
            "skill": n,
            "label": skills[n]["label_en"],
            "hours": skills[n]["hours"],
            "requires": skills[n]["requires"],
            "why": _why(n, closure, direct_required, skills, role["label_en"]),
            "source": skills[n]["source"],
        }
        for n in ordered
    ]
    graph_nodes = [
        {
            "skill": n,
            "label": skills[n]["label_en"],
            "hours": skills[n]["hours"],
            "held": n in held_set,
        }
        for n in sorted(closure)
    ]
    graph_edges = [
        {"from": r, "to": n}
        for n in closure
        for r in skills[n]["requires"]
        if r in closure
    ]
    return {
        "goal": goal,
        "goal_label": role["label_en"],
        "steps": steps,
        "total_hours": sum(s["hours"] for s in steps),
        "graph": {"nodes": graph_nodes, "edges": graph_edges},
    }


def diff_roadmap(held: list[str], goal: str, new_skill: str, skills: dict = SKILLS, roles: dict = ROLES) -> dict:
    if new_skill not in skills:
        raise ValueError(f"unknown skill: {new_skill!r}")

    before = compute_roadmap(held, goal, skills, roles)
    after_held = list(held) if new_skill in held else [*held, new_skill]
    after = compute_roadmap(after_held, goal, skills, roles)

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
        "cause": "learner",
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
