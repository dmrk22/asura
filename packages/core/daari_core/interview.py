"""Pure, evidence-bound interview feedback.

The caller supplies the question and the candidate's own transcript.  This
module never invents an accomplishment: every feedback item keeps an exact
quote from that transcript, which makes the feedback guard mechanically
checkable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Feedback:
    area: str
    quote: str
    guidance: str


@dataclass(frozen=True)
class InterviewReview:
    feedback: tuple[Feedback, ...]
    follow_up: str
    word_count: int
    star: dict[str, bool]


_STAR_MARKERS = {
    "situation": ("when", "while", "context", "team", "project"),
    "task": ("task", "needed to", "responsible", "goal"),
    "action": ("i built", "i made", "i used", "i did", "i created", "i analysed"),
    "result": ("result", "improved", "reduced", "increased", "%", "saved"),
}


def _sentences(transcript: str) -> tuple[str, ...]:
    return tuple(s.strip() for s in re.split(r"(?<=[.!?])\s+", transcript.strip()) if s.strip())


def _quote_for(sentences: tuple[str, ...], markers: tuple[str, ...]) -> str:
    for sentence in sentences:
        if any(marker in sentence.casefold() for marker in markers):
            return sentence
    return sentences[0]


def review(question: str, transcript: str) -> InterviewReview:
    """Return concise feedback that is always anchored to a transcript quote."""
    if not question.strip():
        raise ValueError("question is required")
    sentences = _sentences(transcript)
    if not sentences:
        raise ValueError("transcript is required")

    folded = transcript.casefold()
    star = {name: any(marker in folded for marker in markers) for name, markers in _STAR_MARKERS.items()}
    feedback: list[Feedback] = []
    for area in ("situation", "task", "action", "result"):
        if not star[area]:
            feedback.append(
                Feedback(
                    area=area,
                    quote=_quote_for(sentences, ()),
                    guidance=f"Add one clear {area} detail to make this answer easier to verify.",
                )
            )
    if not feedback:
        feedback.append(
            Feedback(
                area="specificity",
                quote=sentences[0],
                guidance="Keep this concrete structure; add a measurable outcome if one is available.",
            )
        )
    weakest = next((area for area in ("situation", "task", "action", "result") if not star[area]), "result")
    return InterviewReview(
        feedback=tuple(feedback),
        follow_up=f"What is one specific {weakest} detail you would add to this answer?",
        word_count=len(re.findall(r"\b\w+\b", transcript)),
        star=star,
    )
