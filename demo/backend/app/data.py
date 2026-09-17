"""Seed data for the localhost demo — loaded from the REAL sourced taxonomy
committed at data/taxonomy/{skills,roles}.yaml (DAARI_BUILD_PLAN.md §7.1,
docs/DECISIONS.md D17), not invented. Every skill node carries a real
ESCO/NSQF/NPTEL citation — see that file's header for the sourcing note.

Jobs are still a seeded, offline placeholder list (source_url/fetched_at are
NOT live-fetched tonight — see the report to the user), but every job's
required_skills reference the same real taxonomy ids as everything else.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
TAXONOMY_DIR = REPO_ROOT / "data" / "taxonomy"


def _load_skills() -> dict[str, dict]:
    raw = yaml.safe_load((TAXONOMY_DIR / "skills.yaml").read_text())
    return {
        node["id"]: {
            "label_en": node["label_en"],
            "label_te": node.get("label_te", ""),
            "hours": node["hours"],
            "requires": list(node.get("prereqs", [])),
            "source": node["source"],
        }
        for node in raw
    }


def _load_roles() -> dict[str, dict]:
    raw = yaml.safe_load((TAXONOMY_DIR / "roles.yaml").read_text())
    roles = {}
    for role in raw:
        required = role["required_skills"]
        skill_ids = (
            list(required.keys())
            if isinstance(required, dict)
            else [entry["skill_id"] for entry in required]
        )
        roles[role["id"]] = {
            "label_en": role["label_en"],
            "label_te": role.get("label_te", ""),
            "required_skills": skill_ids,
            "source": role["source"],
        }
    return roles


SKILLS: dict[str, dict] = _load_skills()
ROLES: dict[str, dict] = _load_roles()

# Demo personas — synthetic only (Ravi, Priya), per project convention.
# Held skills use the real taxonomy ids.
PROFILES: dict[str, dict] = {
    "priya": {
        "name": "Priya",
        "held": ["spoken_english", "basic_numeracy", "digital_literacy", "python_programming", "sql_querying"],
        "goal": "data_analyst",
    },
    "ravi": {
        "name": "Ravi",
        "held": [],
        "goal": "delivery_executive",
    },
}

# ~10 seeded jobs — offline placeholder listings for tonight's demo (source_url
# is NOT a live fetcher; swap for the real schemes/leads pipeline later).
# required_skills reference the real taxonomy ids above.
JOBS: list[dict] = [
    {
        "id": "job-001",
        "title": "Junior Data Analyst",
        "company": "Andhra Analytics Pvt Ltd",
        "location": "Vijayawada",
        "required_skills": ["sql_querying", "ms_excel_basic", "data_visualization_powerbi", "statistics_fundamentals"],
        "source_url": "https://example-jobs.local/listing/job-001",
    },
    {
        "id": "job-002",
        "title": "Business Intelligence Intern",
        "company": "Krishna Data Systems",
        "location": "Guntur",
        "required_skills": ["sql_querying", "data_visualization_powerbi", "excel_advanced"],
        "source_url": "https://example-jobs.local/listing/job-002",
    },
    {
        "id": "job-003",
        "title": "Reporting Analyst",
        "company": "Godavari Retail Group",
        "location": "Vijayawada",
        "required_skills": ["sql_querying", "data_visualization_tableau", "statistics_fundamentals"],
        "source_url": "https://example-jobs.local/listing/job-003",
    },
    {
        "id": "job-004",
        "title": "Python Data Associate",
        "company": "Sarovar Tech Solutions",
        "location": "Guntur",
        "required_skills": ["python_programming", "data_cleaning", "statistics_fundamentals"],
        "source_url": "https://example-jobs.local/listing/job-004",
    },
    {
        "id": "job-005",
        "title": "Entry-Level Data Analyst",
        "company": "Coastal Insights Co",
        "location": "Vijayawada",
        "required_skills": ["python_programming", "sql_querying", "data_visualization_powerbi", "statistics_fundamentals"],
        "source_url": "https://example-jobs.local/listing/job-005",
    },
    {
        "id": "job-006",
        "title": "Delivery Executive",
        "company": "QuickCart Logistics",
        "location": "Guntur",
        "required_skills": ["two_wheeler_riding", "route_navigation_gps", "delivery_safety_compliance", "cash_reconciliation"],
        "source_url": "https://example-jobs.local/listing/job-006",
    },
    {
        "id": "job-007",
        "title": "Retail Sales Associate",
        "company": "Sri Lakshmi Super Market",
        "location": "Vijayawada",
        "required_skills": ["customer_service_basic", "cash_handling", "time_management"],
        "source_url": "https://example-jobs.local/listing/job-007",
    },
    {
        "id": "job-008",
        "title": "Two-Wheeler Delivery Rider",
        "company": "SpeedyBox Couriers",
        "location": "Tenali",
        "required_skills": ["two_wheeler_riding", "traffic_safety_rules", "local_area_familiarity"],
        "source_url": "https://example-jobs.local/listing/job-008",
    },
    {
        "id": "job-009",
        "title": "Store Cashier",
        "company": "Godavari Retail Group",
        "location": "Guntur",
        "required_skills": ["cash_handling", "cash_reconciliation", "customer_service_basic", "basic_numeracy"],
        "source_url": "https://example-jobs.local/listing/job-009",
    },
    {
        "id": "job-010",
        "title": "Warehouse & Delivery Associate",
        "company": "QuickCart Logistics",
        "location": "Vijayawada",
        "required_skills": ["package_handling_safety", "delivery_safety_compliance", "time_management"],
        "source_url": "https://example-jobs.local/listing/job-010",
    },
]
