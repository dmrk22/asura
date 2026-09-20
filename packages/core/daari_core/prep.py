"""Pure placement-preparation scheduler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PrepDay:
    day: int
    focus: str
    hours: int


def schedule(interview_date: date, today: date, focus: tuple[str, ...]) -> tuple[PrepDay, ...]:
    """Distribute one focused, feasible preparation block across available days."""
    remaining = (interview_date - today).days
    if remaining < 1:
        raise ValueError("interview_date must be after today")
    topics = focus or ("role fundamentals", "mock interview", "review")
    return tuple(
        PrepDay(day=index + 1, focus=topics[index % len(topics)], hours=2)
        for index in range(min(remaining, 14))
    )
