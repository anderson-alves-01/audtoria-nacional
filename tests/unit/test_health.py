from fastapi.testclient import TestClient

from sirta_api.entrypoints.main import create_app


def test_health_returns_implementation_metadata() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["specVersion"] == "0.3.0"
    assert body["implementationVersion"] == "0.3.14"
    assert body["releaseStage"] == "REAL_DATA_PIPELINES_AWAITING_HUMAN_VALIDATION"
    assert response.headers.get("x-trace-id")
