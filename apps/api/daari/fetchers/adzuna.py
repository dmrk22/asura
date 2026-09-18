"""daari.fetchers.adzuna — live India job search, keyed (app_id + app_key).

Currently 401 AUTH_FAIL while the key is re-pasted into .env (2026-09-18) —
this fetcher must degrade to an empty list plus an error string, never crash
a route, on a 401 same as on any other failure.

The request carries `app_id`/`app_key` as query params via httpx's own
`params=` encoding (never hand-concatenated into a URL string). Those
credentials must never reach a rendered card: `source_url` is always
Adzuna's own public `redirect_url` for the listing, or a credential-free
public search link — never the credentialed request URL.
"""

from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import quote

import httpx

from daari.config import settings
from daari.http import get_json, new_client

SOURCE = "adzuna"
URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"


def _public_search_url(q: str) -> str:
    """Credential-free fallback link when a listing has no `redirect_url`."""
    return f"https://www.adzuna.in/jobs/search?q={quote(q)}" if q else "https://www.adzuna.in/"


async def fetch(q: str = "", limit: int = 20) -> tuple[list[dict], str | None]:
    """Never raises: on failure (missing key, 401, network) returns `([], "<reason>")`."""
    if not (settings.ADZUNA_APP_ID and settings.ADZUNA_APP_KEY):
        return [], "adzuna_skipped: no_api_key"

    fetched_at = datetime.now(UTC).isoformat()  # stamped once, carried to every record
    params: dict[str, object] = {
        "app_id": settings.ADZUNA_APP_ID,
        "app_key": settings.ADZUNA_APP_KEY,
        "results_per_page": limit,
    }
    if q:
        params["what"] = q

    try:
        async with new_client() as client:
            data = await get_json(client, URL, params=params)
    except httpx.HTTPStatusError as exc:
        return [], f"adzuna_http_{exc.response.status_code}"
    except (httpx.RequestError, ValueError) as exc:
        return [], f"adzuna_unreachable: {type(exc).__name__}"

    results = data.get("results") if isinstance(data, dict) else None
    if not results:
        return [], None

    records = []
    for job in results:
        loc = job.get("location") or {}
        records.append(
            {
                "id": f"adzuna-{job.get('id')}",
                "title": job.get("title", ""),
                "org": (job.get("company") or {}).get("display_name", ""),
                "location": loc.get("display_name", ""),
                "pay": f"{job['salary_min']:.0f}+" if job.get("salary_min") else None,
                "description": job.get("description", ""),
                "source": SOURCE,
                # Adzuna's own public listing link. Never the request URL
                # (which carries app_id/app_key) and never bare — a listing
                # without a redirect_url falls back to a credential-free
                # public search link, not the credentialed one.
                "source_url": job.get("redirect_url") or _public_search_url(q),
                "fetched_at": fetched_at,
                "is_live": True,
            }
        )
    return records, None
