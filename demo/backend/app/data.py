"""Hardcoded seed data for the localhost demo. No network, no DB — everything here.

Two goal skills anchor the two demo personas:
  - "data_analyst_portfolio" (Priya's goal)
  - "delivery_retail_ready"  (Ravi's goal)
"""

# skill_id -> {hours: int, requires: list[skill_id]}
SKILLS: dict[str, dict] = {
    # --- shared foundation ---
    "spoken_english": {"hours": 15, "requires": []},
    "basic_numeracy": {"hours": 10, "requires": []},
    "digital_literacy": {"hours": 8, "requires": []},
    "teamwork": {"hours": 6, "requires": []},
    "time_management": {"hours": 8, "requires": []},
    "workplace_communication": {"hours": 6, "requires": ["spoken_english"]},

    # --- data analyst track ---
    "excel_basics": {"hours": 12, "requires": ["digital_literacy"]},
    "excel_advanced": {"hours": 15, "requires": ["excel_basics"]},
    "database_fundamentals": {"hours": 15, "requires": []},
    "sql": {"hours": 20, "requires": []},
    "sql_advanced": {"hours": 15, "requires": ["sql"]},
    "python": {"hours": 30, "requires": []},
    "pandas": {"hours": 15, "requires": ["python"]},
    "numpy": {"hours": 10, "requires": ["python"]},
    "statistics": {"hours": 20, "requires": []},
    "problem_solving_analytical": {"hours": 10, "requires": []},
    "data_cleaning": {"hours": 12, "requires": ["pandas"]},
    "data_visualization_matplotlib": {"hours": 10, "requires": ["pandas"]},
    "power_bi": {"hours": 15, "requires": ["sql"]},
    "tableau": {"hours": 15, "requires": ["sql"]},
    "data_storytelling": {"hours": 8, "requires": ["data_visualization_matplotlib"]},
    "git_version_control": {"hours": 8, "requires": []},
    "data_analyst_portfolio": {
        "hours": 10,
        "requires": ["pandas", "power_bi", "statistics"],
    },

    # --- delivery / retail track ---
    "traffic_safety_rules": {"hours": 6, "requires": []},
    "two_wheeler_riding": {"hours": 10, "requires": []},
    "driving_license_prep": {"hours": 12, "requires": ["traffic_safety_rules"]},
    "vehicle_maintenance_basic": {"hours": 8, "requires": ["two_wheeler_riding"]},
    "mobile_app_usage": {"hours": 5, "requires": ["digital_literacy"]},
    "route_navigation_gps": {"hours": 6, "requires": ["mobile_app_usage"]},
    "local_area_familiarity": {"hours": 10, "requires": ["route_navigation_gps"]},
    "cash_handling": {"hours": 8, "requires": ["basic_numeracy"]},
    "cash_reconciliation": {"hours": 6, "requires": ["cash_handling"]},
    "customer_service_basic": {"hours": 10, "requires": ["spoken_english"]},
    "customer_complaint_handling": {"hours": 8, "requires": ["customer_service_basic"]},
    "inventory_basics": {"hours": 10, "requires": ["basic_numeracy"]},
    "pos_billing_systems": {"hours": 8, "requires": ["digital_literacy"]},
    "product_knowledge_retail": {"hours": 10, "requires": []},
    "package_handling_safety": {"hours": 6, "requires": []},
    "delivery_safety_compliance": {
        "hours": 8,
        "requires": ["traffic_safety_rules", "package_handling_safety"],
    },
    "delivery_retail_ready": {
        "hours": 5,
        "requires": [
            "two_wheeler_riding",
            "cash_reconciliation",
            "customer_complaint_handling",
            "delivery_safety_compliance",
            "pos_billing_systems",
        ],
    },
}

# Demo personas — synthetic only, per project convention (no real people/data).
PROFILES: dict[str, dict] = {
    "priya": {
        "name": "Priya",
        "held": ["spoken_english", "basic_numeracy", "digital_literacy", "python", "sql"],
        "goal": "data_analyst_portfolio",
    },
    "ravi": {
        "name": "Ravi",
        "held": [],
        "goal": "delivery_retail_ready",
    },
}

# ~10 seeded jobs. source_url/fetched_at are placeholders for tonight's offline
# demo — swap for a real fetcher's output later (see report to user).
JOBS: list[dict] = [
    {
        "id": "job-001",
        "title": "Junior Data Analyst",
        "company": "Andhra Analytics Pvt Ltd",
        "location": "Vijayawada",
        "required_skills": ["sql", "excel_basics", "power_bi", "statistics"],
        "source_url": "https://example-jobs.local/listing/job-001",
    },
    {
        "id": "job-002",
        "title": "Business Intelligence Intern",
        "company": "Krishna Data Systems",
        "location": "Guntur",
        "required_skills": ["sql", "power_bi", "excel_advanced"],
        "source_url": "https://example-jobs.local/listing/job-002",
    },
    {
        "id": "job-003",
        "title": "Reporting Analyst",
        "company": "Godavari Retail Group",
        "location": "Vijayawada",
        "required_skills": ["sql", "tableau", "data_storytelling", "statistics"],
        "source_url": "https://example-jobs.local/listing/job-003",
    },
    {
        "id": "job-004",
        "title": "Python Data Associate",
        "company": "Sarovar Tech Solutions",
        "location": "Guntur",
        "required_skills": ["python", "pandas", "data_cleaning", "numpy"],
        "source_url": "https://example-jobs.local/listing/job-004",
    },
    {
        "id": "job-005",
        "title": "Entry-Level Data Analyst",
        "company": "Coastal Insights Co",
        "location": "Vijayawada",
        "required_skills": ["python", "sql", "pandas", "power_bi", "statistics"],
        "source_url": "https://example-jobs.local/listing/job-005",
    },
    {
        "id": "job-006",
        "title": "Delivery Executive",
        "company": "QuickCart Logistics",
        "location": "Guntur",
        "required_skills": [
            "two_wheeler_riding",
            "route_navigation_gps",
            "delivery_safety_compliance",
            "cash_reconciliation",
        ],
        "source_url": "https://example-jobs.local/listing/job-006",
    },
    {
        "id": "job-007",
        "title": "Retail Sales Associate",
        "company": "Sri Lakshmi Super Market",
        "location": "Vijayawada",
        "required_skills": [
            "customer_service_basic",
            "pos_billing_systems",
            "inventory_basics",
            "product_knowledge_retail",
        ],
        "source_url": "https://example-jobs.local/listing/job-007",
    },
    {
        "id": "job-008",
        "title": "Two-Wheeler Delivery Rider",
        "company": "SpeedyBox Couriers",
        "location": "Tenali",
        "required_skills": [
            "two_wheeler_riding",
            "traffic_safety_rules",
            "local_area_familiarity",
        ],
        "source_url": "https://example-jobs.local/listing/job-008",
    },
    {
        "id": "job-009",
        "title": "Store Cashier",
        "company": "Godavari Retail Group",
        "location": "Guntur",
        "required_skills": [
            "cash_handling",
            "cash_reconciliation",
            "customer_service_basic",
            "basic_numeracy",
        ],
        "source_url": "https://example-jobs.local/listing/job-009",
    },
    {
        "id": "job-010",
        "title": "Warehouse & Delivery Associate",
        "company": "QuickCart Logistics",
        "location": "Vijayawada",
        "required_skills": [
            "package_handling_safety",
            "inventory_basics",
            "delivery_safety_compliance",
            "time_management",
        ],
        "source_url": "https://example-jobs.local/listing/job-010",
    },
]
