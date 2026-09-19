"""Scam Shield tests (§7.4, safety.md guard 3): a badge without reasons is a bug.

Every positive rule fixture adds exactly one trigger on top of a clean baseline
listing, so a fired rule is attributable to that one rule and not to overlap
with another.
"""

from __future__ import annotations

from daari_core import scam

CLEAN = {
    "title": "Warehouse packing associate",
    "description": "Sort and pack orders on the evening shift.",
    "org": "Sri Lakshmi Logistics Pvt Ltd",
    "pay": "₹18,000/month",
    "contact": "hr@srilakshmilogistics.com",
    "source_url": "https://srilakshmilogistics.com/careers/42",
    "apply_url": "https://srilakshmilogistics.com/careers/42/apply",
}


def _full_text(listing: dict) -> str:
    return " ".join(str(v) for v in listing.values() if v)


def test_clean_listing_scores_zero_with_no_reasons():
    result = scam.score(CLEAN)
    assert result.score == 0.0
    assert result.reasons == ()
    assert result.band == "clear"


def test_upfront_fee_rule_fires_and_quote_is_a_real_substring():
    listing = {**CLEAN, "description": CLEAN["description"] + " Pay a registration charge to apply."}
    result = scam.score(listing)
    rule_names = {r.rule for r in result.reasons}
    assert "upfront_fee" in rule_names
    reason = next(r for r in result.reasons if r.rule == "upfront_fee")
    assert reason.weight == 0.45
    assert reason.quote in _full_text(listing)


def test_personal_contact_only_rule_fires():
    listing = {**CLEAN, "contact": "whatsapp only 9876543210", "source_url": "", "apply_url": ""}
    result = scam.score(listing)
    reason = next(r for r in result.reasons if r.rule == "personal_contact_only")
    assert reason.weight == 0.25
    assert reason.quote in _full_text(listing)


def test_personal_contact_rule_stays_quiet_when_org_domain_present():
    result = scam.score(CLEAN)
    assert "personal_contact_only" not in {r.rule for r in result.reasons}


def test_no_org_rule_fires_on_missing_org():
    listing = {**CLEAN, "org": ""}
    result = scam.score(listing)
    assert "no_org" in {r.rule for r in result.reasons}


def test_no_org_rule_fires_on_confidential():
    listing = {**CLEAN, "org": "Confidential"}
    result = scam.score(listing)
    reason = next(r for r in result.reasons if r.rule == "no_org")
    assert reason.weight == 0.15


def test_pay_out_of_band_rule_fires():
    listing = {**CLEAN, "pay": "₹50,00,000/month"}
    result = scam.score(listing)
    reason = next(r for r in result.reasons if r.rule == "pay_out_of_band")
    assert reason.weight == 0.2
    assert reason.quote in _full_text(listing)


def test_pay_within_custom_band_stays_quiet():
    listing = {**CLEAN, "pay": "₹9,00,000/month"}
    result = scam.score(listing, pay_band=(3000.0, 1_500_000.0))
    assert "pay_out_of_band" not in {r.rule for r in result.reasons}


def test_unverifiable_url_rule_fires_on_missing_source_url():
    listing = {**CLEAN, "source_url": ""}
    result = scam.score(listing)
    assert "unverifiable_url" in {r.rule for r in result.reasons}


def test_unverifiable_url_rule_fires_on_http_shortener():
    listing = {**CLEAN, "source_url": "http://bit.ly/abc123"}
    result = scam.score(listing)
    reason = next(r for r in result.reasons if r.rule == "unverifiable_url")
    assert reason.quote in _full_text(listing)


def test_unverifiable_url_rule_stays_quiet_on_https():
    result = scam.score(CLEAN)
    assert "unverifiable_url" not in {r.rule for r in result.reasons}


def test_urgency_combo_rule_fires():
    listing = {**CLEAN, "description": CLEAN["description"] + " Immediate joining, no interview."}
    result = scam.score(listing)
    reason = next(r for r in result.reasons if r.rule == "urgency_no_interview")
    assert reason.weight == 0.2
    assert reason.quote in _full_text(listing)


def test_score_is_clamped_to_one_when_every_rule_fires():
    listing = {
        "title": "URGENT hiring",
        "description": "Immediate joining, no interview, unlimited earning. Pay a registration charge to apply.",
        "org": "",
        "pay": "₹50,00,000/month",
        "contact": "whatsapp 9876543210",
        "source_url": "http://bit.ly/xyz",
        "apply_url": "http://bit.ly/xyz",
    }
    result = scam.score(listing)
    assert result.score == 1.0
    assert result.band == "red"
    assert len(result.reasons) == 6


def test_band_thresholds():
    assert scam.score(CLEAN).band == "clear"
    listing = {**CLEAN, "org": ""}  # 0.15 -> clear still
    assert scam.score(listing).band == "clear"
    listing = {**CLEAN, "org": "", "source_url": ""}  # 0.15 + 0.15 = 0.3 -> check
    assert scam.score(listing).band == "check"
    listing = {
        **CLEAN,
        "description": CLEAN["description"] + " Pay a registration charge to apply.",
        "org": "",
    }  # 0.45 + 0.15 = 0.6 -> red
    assert scam.score(listing).band == "red"


def test_every_reason_quote_is_a_real_substring_of_the_listing():
    listing = {
        "title": "URGENT hiring",
        "description": "Immediate joining, no interview, unlimited earning. Pay a registration charge to apply.",
        "org": "",
        "pay": "₹50,00,000/month",
        "contact": "whatsapp 9876543210",
        "source_url": "http://bit.ly/xyz",
        "apply_url": "http://bit.ly/xyz",
    }
    result = scam.score(listing)
    full_text = _full_text(listing)
    for reason in result.reasons:
        assert reason.quote in full_text or reason.quote == "", reason
