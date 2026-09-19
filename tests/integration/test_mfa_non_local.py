import os

from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)
from sirta_api.config import get_settings


def _staging_env(monkeypatch) -> dict[str, str | None]:
    previous = {
        "ENVIRONMENT": os.environ.get("ENVIRONMENT"),
        "DATABASE_URL": os.environ.get("DATABASE_URL"),
        "S3_SECRET_KEY": os.environ.get("S3_SECRET_KEY"),
    }
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://sirta:staging_secret@localhost:55432/sirta",
    )
    monkeypatch.setenv("S3_SECRET_KEY", "staging_s3_secret")
    get_settings.cache_clear()
    return previous


def _restore_env(monkeypatch, previous: dict[str, str | None]) -> None:
    for key, value in previous.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    get_settings.cache_clear()


def test_non_local_without_mfa_is_forbidden(api_client, monkeypatch) -> None:
    previous = _staging_env(monkeypatch)
    try:
        response = api_client.get(
            "/v1/diagnosis",
            headers=auth_headers(
                subject=USER_ANALYST_ALPHA,
                tenant_id=TENANT_ALPHA,
                territory_id=TERRITORY_ALPHA_CENTRO,
                purpose_id=PURPOSE_ALPHA_ACTIVE,
            ),
        )
        assert response.status_code == 403
        detail = str(response.json().get("detail", ""))
        assert "MFA" in detail or "mfa" in detail.lower()
    finally:
        _restore_env(monkeypatch, previous)


def test_non_local_with_mfa_claim_is_allowed(api_client, monkeypatch) -> None:
    previous = _staging_env(monkeypatch)
    try:
        response = api_client.get(
            "/v1/diagnosis",
            headers=auth_headers(
                subject=USER_ANALYST_ALPHA,
                tenant_id=TENANT_ALPHA,
                territory_id=TERRITORY_ALPHA_CENTRO,
                purpose_id=PURPOSE_ALPHA_ACTIVE,
                mfa=True,
            ),
        )
        assert response.status_code == 200
    finally:
        _restore_env(monkeypatch, previous)
