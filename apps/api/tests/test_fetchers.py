"""daari.fetchers.* — each fetcher never raises, always stamps `source`,
`source_url`, `fetched_at`, `is_live`, and never leaks a credentialed
request URL into a rendered `source_url`.

httpx is never hit here: each fetcher's own `get_json` call is monkeypatched
(no `respx` dependency in this project) so the suite never depends on the
live network.
"""

from __future__ import annotations

import httpx
import pytest

from daari.fetchers import adzuna, myscheme, nominatim, remotive

# --- remotive -------------------------------------------------------------


@pytest.mark.asyncio
async def test_remotive_normalises_jobs_with_provenance(monkeypatch):
    async def fake_get_json(client, url, **kwargs):
        return {
            "jobs": [
                {
                    "id": 42,
                    "title": "Data Analyst",
                    "company_name": "Acme",
                    "candidate_required_location": "India",
                    "salary": "10-15 LPA",
                    "url": "https://remotive.com/remote-jobs/data-analyst-42",
                    "description": "SQL and Python required.",
                }
            ]
        }

    monkeypatch.setattr(remotive, "get_json", fake_get_json)
    records, error = await remotive.fetch(limit=5)

    assert error is None
    assert len(records) == 1
    record = records[0]
    assert record["source"] == "remotive"
    assert record["source_url"] == "https://remotive.com/remote-jobs/data-analyst-42"
    assert record["fetched_at"]
    assert record["is_live"] is True


@pytest.mark.asyncio
async def test_remotive_degrades_on_network_failure_instead_of_raising(monkeypatch):
    async def fake_get_json(client, url, **kwargs):
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(remotive, "get_json", fake_get_json)
    records, error = await remotive.fetch()

    assert records == []
    assert error is not None


@pytest.mark.asyncio
async def test_remotive_all_records_share_one_fetched_at_stamp(monkeypatch):
    """Two-clock bug guard: fetched_at is read once, not once per record."""

    async def fake_get_json(client, url, **kwargs):
        return {"jobs": [{"id": 1, "title": "A"}, {"id": 2, "title": "B"}]}

    monkeypatch.setattr(remotive, "get_json", fake_get_json)
    records, _ = await remotive.fetch()

    assert len({r["fetched_at"] for r in records}) == 1


# --- adzuna -----------------------------------------------------------


@pytest.mark.asyncio
async def test_adzuna_skips_without_crashing_when_key_is_missing(monkeypatch):
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_ID", None)
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_KEY", None)

    records, error = await adzuna.fetch(q="analyst")

    assert records == []
    assert "no_api_key" in error


@pytest.mark.asyncio
async def test_adzuna_degrades_on_401_instead_of_raising(monkeypatch):
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_ID", "id")
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_KEY", "key")

    async def fake_get_json(client, url, **kwargs):
        request = httpx.Request("GET", url)
        response = httpx.Response(401, request=request)
        raise httpx.HTTPStatusError("401", request=request, response=response)

    monkeypatch.setattr(adzuna, "get_json", fake_get_json)
    records, error = await adzuna.fetch(q="analyst")

    assert records == []
    assert "401" in error


@pytest.mark.asyncio
async def test_adzuna_source_url_never_carries_the_credentialed_request_url(monkeypatch):
    """Security regression: a listing's `source_url` must never be the
    request URL, which carries `app_id`/`app_key` as query params."""
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_ID", "secret-id")
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_KEY", "secret-key")

    async def fake_get_json(client, url, **kwargs):
        assert "secret-id" not in url  # credentials travel via params=, not the URL
        return {
            "results": [
                {"id": 1, "title": "No redirect", "company": {}, "location": {}},
                {
                    "id": 2,
                    "title": "Has redirect",
                    "company": {},
                    "location": {},
                    "redirect_url": "https://www.adzuna.in/land/ad/2",
                },
            ]
        }

    monkeypatch.setattr(adzuna, "get_json", fake_get_json)
    records, error = await adzuna.fetch(q="analyst")

    assert error is None
    assert len(records) == 2
    no_redirect, has_redirect = records
    assert "secret-id" not in no_redirect["source_url"]
    assert "secret-key" not in no_redirect["source_url"]
    assert no_redirect["source_url"] == "https://www.adzuna.in/jobs/search?q=analyst"
    assert has_redirect["source_url"] == "https://www.adzuna.in/land/ad/2"


@pytest.mark.asyncio
async def test_adzuna_request_uses_params_not_a_hand_built_query_string(monkeypatch):
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_ID", "id")
    monkeypatch.setattr(adzuna.settings, "ADZUNA_APP_KEY", "key")

    seen = {}

    async def fake_get_json(client, url, *, params=None, headers=None, cache_ttl_s=900.0):
        seen["url"] = url
        seen["params"] = params
        return {"results": []}

    monkeypatch.setattr(adzuna, "get_json", fake_get_json)
    await adzuna.fetch(q="analyst")

    assert seen["url"] == adzuna.URL
    assert seen["params"]["app_id"] == "id"
    assert seen["params"]["what"] == "analyst"


# --- myscheme -----------------------------------------------------------


@pytest.mark.asyncio
async def test_myscheme_normalises_hits_with_provenance(monkeypatch):
    async def fake_get_json(client, url, **kwargs):
        return {
            "data": {
                "hits": {
                    "items": [
                        {
                            "fields": {
                                "schemeId": "S1",
                                "schemeName": "Test Scheme",
                                "slug": "test-scheme",
                                "nodalMinistryName": "Ministry of Testing",
                            }
                        }
                    ]
                }
            }
        }

    monkeypatch.setattr(myscheme, "get_json", fake_get_json)
    records, error = await myscheme.fetch(q="income")

    assert error is None
    assert len(records) == 1
    assert records[0]["source"] == "myscheme"
    assert records[0]["source_url"] == "https://www.myscheme.gov.in/schemes/test-scheme"
    assert records[0]["fetched_at"]


@pytest.mark.asyncio
async def test_myscheme_skips_without_crashing_when_key_missing(monkeypatch):
    monkeypatch.setattr(myscheme, "get_sources", dict)
    records, error = await myscheme.fetch(q="income")

    assert records == []
    assert "no_api_key" in error


# --- nominatim -----------------------------------------------------------


@pytest.mark.asyncio
async def test_nominatim_normalises_a_result(monkeypatch):
    async def fake_get_json(client, url, **kwargs):
        return [{"lat": "16.30", "lon": "80.44", "display_name": "Guntur, Andhra Pradesh, India"}]

    monkeypatch.setattr(nominatim, "get_json", fake_get_json)
    records, error = await nominatim.fetch(q="Guntur")

    assert error is None
    assert records[0]["lat"] == 16.30
    assert records[0]["source"] == "nominatim"


@pytest.mark.asyncio
async def test_nominatim_degrades_when_nothing_found(monkeypatch):
    async def fake_get_json(client, url, **kwargs):
        return []

    monkeypatch.setattr(nominatim, "get_json", fake_get_json)
    records, error = await nominatim.fetch(q="nowhere")

    assert records == []
    assert error is None
