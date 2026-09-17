"""The setup exit criterion, as a test: /health reports db, redis and the provider chain."""
from fastapi.testclient import TestClient

from nadi.main import app


def test_health_reports_every_dependency():
    with TestClient(app) as client:
        body = client.get("/health").json()
    assert set(body) == {"sha", "db", "redis", "llm"}
    assert body["db"] == "ok", f"postgres not reachable: {body['db']}"
    assert body["redis"] == "ok", f"redis not reachable: {body['redis']}"
    # The chain always ends in cache, so the demo survives a dead network.
    assert body["llm"][-1] == "cache"
