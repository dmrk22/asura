"""In-process call counters, per persona, per engine.

`/evidence` reads this to prove the shared-engine claim live: both persona
routes call the same daari_core functions, and the counters move because a
real call happened, not because a page decorates a number. Pure — no clock,
no I/O, no randomness. Counts live only in this process's memory and reset
on restart; that is the point, they are read from the live process.
"""

from collections import defaultdict

_counts: dict[tuple[str, str], int] = defaultdict(int)


def count(persona: str, engine: str) -> None:
    """Record one call to `engine` made on behalf of `persona`."""
    _counts[(persona, engine)] += 1


def snapshot() -> dict[str, dict[str, int]]:
    """Return `{persona: {engine: count}}` for every call recorded so far."""
    out: dict[str, dict[str, int]] = defaultdict(dict)
    for (persona, engine), n in _counts.items():
        out[persona][engine] = n
    return dict(out)
