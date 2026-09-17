"""Fixture: a persona adapter that violates the one-engine rule.

Exists only so test_shared_engine.py can prove its AST scan actually
catches a violation, instead of trivially passing on an empty directory.
Defines `match` locally (should be imported from daari_core) and does
arithmetic on a score-shaped value — both are things a persona route
must never do.
"""


def match(profile, jobs):
    coverage = 0.8
    gap_cost = 0.2
    score = coverage * 0.4 - gap_cost * 0.2
    return score
