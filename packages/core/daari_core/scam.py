"""daari_core.scam — Scam Shield: a rules-first, explainable score over a listing (§7.4).

Pure: stdlib only (re). No I/O, no clock, no randomness (core.md).

safety.md guard 3: "a badge without reasons is a bug." Every rule that fires
carries the exact substring of the listing that triggered it, in the same
spirit as `roadmap.why` and `match.reasons` — a score with nothing behind it
is exactly the kind of number this project refuses to show.

Rules-first per §7.4: this is the whole score. The LLM's second opinion (in
apps/api, not here) may add at most 0.2 on top, with its own quoted reason —
that ceiling and that quote requirement live outside this module.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

RED_THRESHOLD = 0.5
CHECK_THRESHOLD = 0.3

# A plausible monthly INR pay band for the demo's target roles. Module constant,
# not a magic number in the function body — a caller doing real ranking passes
# its own `pay_band`.
DEFAULT_PAY_BAND: tuple[float, float] = (3000.0, 150_000.0)

TEXT_FIELDS = ("title", "description", "desc", "org", "pay", "contact", "source_url", "apply_url")

_FEE_RE = re.compile(
    r"registration charge|security deposit|processing fee|upfront fee|pay\s*₹\s?[\d,]+\s*to apply",
    re.IGNORECASE,
)
_PERSONAL_CONTACT_RE = re.compile(r"whatsapp|telegram|gmail\.com", re.IGNORECASE)
_ORG_DOMAIN_RE = re.compile(r"@(?!gmail\.com)[a-z0-9.-]+\.[a-z]{2,}", re.IGNORECASE)
_EMPTY_ORG_VALUES = {"", "private", "confidential"}
_PAY_NUM_RE = re.compile(r"₹?\s?([\d,]+(?:\.\d+)?)")
_SHORTENER_HOSTS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "ow.ly"}
_URGENCY_RE = re.compile(r"immediate joining|no interview|unlimited earning", re.IGNORECASE)


@dataclass(frozen=True)
class Reason:
    rule: str
    weight: float
    quote: str


@dataclass(frozen=True)
class ScamResult:
    score: float
    reasons: tuple[Reason, ...]
    band: Literal["clear", "check", "red"]


def _full_text(listing: Mapping[str, Any]) -> str:
    return " \n ".join(str(listing[f]) for f in TEXT_FIELDS if listing.get(f))


def _fee_rule(listing: Mapping[str, Any]) -> Reason | None:
    m = _FEE_RE.search(_full_text(listing))
    return Reason("upfront_fee", 0.45, m.group(0)) if m else None


def _personal_contact_rule(listing: Mapping[str, Any]) -> Reason | None:
    contact = str(listing.get("contact") or "")
    m = _PERSONAL_CONTACT_RE.search(contact)
    if m and not _ORG_DOMAIN_RE.search(_full_text(listing)):
        return Reason("personal_contact_only", 0.25, m.group(0))
    return None


def _no_org_rule(listing: Mapping[str, Any]) -> Reason | None:
    org = listing.get("org")
    normalised = str(org).strip().lower() if org else ""
    if normalised in _EMPTY_ORG_VALUES:
        return Reason("no_org", 0.15, str(org) if org else "")
    return None


def _pay_band_rule(listing: Mapping[str, Any], pay_band: tuple[float, float]) -> Reason | None:
    pay = listing.get("pay")
    if not pay:
        return None
    m = _PAY_NUM_RE.search(str(pay))
    if not m:
        return None
    try:
        value = float(m.group(1).replace(",", ""))
    except ValueError:
        return None
    low, high = pay_band
    if value < low or value > high:
        return Reason("pay_out_of_band", 0.2, m.group(0))
    return None


def _unverifiable_url_rule(listing: Mapping[str, Any]) -> Reason | None:
    url = listing.get("source_url")
    if not url:
        return Reason("unverifiable_url", 0.15, "")
    if url.startswith("http://"):
        host = url[len("http://") :].split("/")[0].lower()
        if host in _SHORTENER_HOSTS:
            return Reason("unverifiable_url", 0.15, url)
    return None


def _urgency_rule(listing: Mapping[str, Any]) -> Reason | None:
    m = _URGENCY_RE.search(_full_text(listing))
    return Reason("urgency_no_interview", 0.2, m.group(0)) if m else None


def score(listing: Mapping[str, Any], *, pay_band: tuple[float, float] = DEFAULT_PAY_BAND) -> ScamResult:
    """Rules-first scam score, never a silent block (safety.md guard 3).

    Every triggered rule adds its fixed weight; the total is clamped to 1.0.
    Band: >= 0.5 "red", >= 0.3 "check", else "clear" — "check" is a nudge to
    look closer, never a block.
    """
    checks = (
        _fee_rule(listing),
        _personal_contact_rule(listing),
        _no_org_rule(listing),
        _pay_band_rule(listing, pay_band),
        _unverifiable_url_rule(listing),
        _urgency_rule(listing),
    )
    reasons = tuple(r for r in checks if r is not None)
    total = min(1.0, sum(r.weight for r in reasons))
    band: Literal["clear", "check", "red"] = (
        "red" if total >= RED_THRESHOLD else "check" if total >= CHECK_THRESHOLD else "clear"
    )
    return ScamResult(score=round(total, 4), reasons=reasons, band=band)
