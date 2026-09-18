from pathlib import Path


def test_compose_defines_local_stack_without_cloud_providers() -> None:
    text = Path("compose.yaml").read_text(encoding="utf-8")
    for service in ("postgres:", "redis:", "minio:", "keycloak:", "api:", "worker:", "web:"):
        assert service in text
    lowered = text.lower()
    assert "googleapis" not in lowered
    assert "amazonaws.com" not in lowered
    assert "terraform" not in lowered
    assert "cloudsql" not in lowered
