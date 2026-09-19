"""daari.fetchers.nominatim — live geocoding, OpenStreetMap Nominatim.

Verified live 2026-09-18: 200 with a contact User-Agent. Polite-limited and
15-minute cached by `daari.http.get_json` like every other fetcher.
"""

from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import quote

import httpx

from daari.http import get_json, new_client

SOURCE = "nominatim"
URL_TEMPLATE = "https://nominatim.openstreetmap.org/search?q={q}&format=jsonv2&limit={limit}"


async def fetch(q: str, limit: int = 1) -> tuple[list[dict], str | None]:
    """Never raises: on failure returns `([], "<reason>")`."""
    fetched_at = datetime.now(UTC).isoformat()  # stamped once, carried to every record
    url = URL_TEMPLATE.format(q=quote(q), limit=limit)
    try:
        async with new_client() as client:
            data = await get_json(client, url)
    except httpx.HTTPStatusError as exc:
        return [], f"nominatim_http_{exc.response.status_code}"
    except (httpx.RequestError, ValueError) as exc:
        return [], f"nominatim_unreachable: {type(exc).__name__}"

    if not isinstance(data, list) or not data:
        return [], None

    records = []
    for item in data:
        records.append(
            {
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
                "display_name": item.get("display_name", ""),
                "source": SOURCE,
                "source_url": url,
                "fetched_at": fetched_at,
            }
        )
    return records, None
