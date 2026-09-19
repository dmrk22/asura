"""daari.fetchers.remotive — live remote job listings, no key required.

Verified live 2026-09-18: 200, but only with a browser User-Agent (`daari.http`
sets one on every request this fetcher makes).
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from daari.http import get_json, new_client

SOURCE = "remotive"
URL_TEMPLATE = "https://remotive.com/api/remote-jobs?limit={limit}"


async def fetch(limit: int = 20) -> tuple[list[dict], str | None]:
    """Never raises: on failure returns `([], "<reason>")`."""
    fetched_at = datetime.now(UTC).isoformat()  # stamped once, carried to every record
    url = URL_TEMPLATE.format(limit=limit)
    try:
        async with new_client() as client:
            data = await get_json(client, url)
    except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as exc:
        return [], f"remotive_unreachable: {type(exc).__name__}"

    jobs = data.get("jobs") if isinstance(data, dict) else None
    if not jobs:
        return [], None

    records = []
    for job in jobs:
        records.append(
            {
                "id": f"remotive-{job.get('id')}",
                "title": job.get("title", ""),
                "org": job.get("company_name", ""),
                "location": job.get("candidate_required_location", ""),
                "pay": job.get("salary") or None,
                "description": job.get("description", ""),
                "source": SOURCE,
                "source_url": job.get("url") or url,
                "fetched_at": fetched_at,
                "is_live": True,
            }
        )
    return records, None
