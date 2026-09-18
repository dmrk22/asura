"""daari.fetchers.myscheme — live government scheme search, myscheme v6.

Verified live 2026-09-18: 200, but needs ALL THREE of `x-api-key`, a browser
User-Agent, and `Referer: https://www.myscheme.gov.in/`. v4 and v5 now
return 500 — v6 only. The api-key is public site config (docs/DECISIONS.md
D10), read from `data/sources.yaml`, not a secret and not in .env.
"""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from daari.http import get_json, new_client
from daari.sources_config import get_sources

SOURCE = "myscheme"
URL_TEMPLATE = (
    "https://api.myscheme.gov.in/search/v6/schemes"
    "?lang=en&q=%5B%5D&keyword={keyword}&sort=&from=0&size={limit}"
)
REFERER = "https://www.myscheme.gov.in/"


async def fetch(q: str, limit: int = 20) -> tuple[list[dict], str | None]:
    """Never raises: on failure returns `([], "<reason>")`."""
    api_key = get_sources().get("myscheme", {}).get("x_api_key")
    if not api_key:
        return [], "myscheme_skipped: no_api_key_in_sources_yaml"

    fetched_at = datetime.now(UTC).isoformat()  # stamped once, carried to every record
    url = URL_TEMPLATE.format(keyword=q, limit=limit)
    try:
        async with new_client() as client:
            data = await get_json(client, url, headers={"x-api-key": api_key, "Referer": REFERER})
    except httpx.HTTPStatusError as exc:
        return [], f"myscheme_http_{exc.response.status_code}"
    except (httpx.RequestError, ValueError) as exc:
        return [], f"myscheme_unreachable: {type(exc).__name__}"

    hits = (((data or {}).get("data") or {}).get("hits") or {}).get("items") or []
    if not hits:
        return [], None

    records = []
    for item in hits:
        fields = item.get("fields") or item
        scheme_id = fields.get("schemeId") or fields.get("slug") or item.get("_id", "")
        records.append(
            {
                "id": f"myscheme-{scheme_id}",
                "name": fields.get("schemeName", ""),
                "description": fields.get("schemeShortTitle") or fields.get("briefDescription") or "",
                "ministry": fields.get("nodalMinistryName", ""),
                "source": SOURCE,
                "source_url": f"https://www.myscheme.gov.in/schemes/{fields.get('slug', scheme_id)}",
                "fetched_at": fetched_at,
                "is_live": True,
            }
        )
    return records, None
