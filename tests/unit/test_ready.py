from fastapi.testclient import TestClient

from sirta_api.entrypoints.main import create_app


def test_ready_returns_503_when_database_is_unavailable(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://sirta:sirta_local_only@127.0.0.1:1/sirta",
    )
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:1/0")
    from sirta_api.config import get_settings

    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["status"] == 503
    assert body["title"] == "Service Unavailable"
    assert "traceId" in body
    assert "sirta_local_only" not in response.text
