from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)


def test_public_open_session_disabled_by_default(api_client) -> None:
    response = api_client.get("/v1/auth/public-open-session")
    assert response.status_code == 403


def test_dashboard_works_with_public_open_session(api_client, monkeypatch) -> None:
    monkeypatch.setenv("SIRTA_PUBLIC_OPEN_UI_BOOTSTRAP", "true")
    monkeypatch.setenv("OIDC_SIGNING_KEY_PATH", "tests/fixtures/jwt/private.pem")
    monkeypatch.setenv("OIDC_JWKS_PATH", "tests/fixtures/jwt/jwks.json")
    from sirta_api.config import get_settings

    get_settings.cache_clear()
    session = api_client.get("/v1/auth/public-open-session")
    assert session.status_code == 200
    body = session.json()
    assert body["createsTaxCredit"] is False
    headers = {
        "Authorization": f"Bearer {body['accessToken']}",
        "X-Territory-Id": body["territoryId"],
        "X-Purpose-Id": body["purposeId"],
    }
    dashboard = api_client.get("/v1/dashboards/executivo", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["id"] == "executivo"
    assert dashboard.json()["createsTaxCredit"] is False
    # seeded analyst path still works
    analyst = api_client.get(
        "/v1/dashboards/cobranca",
        headers=auth_headers(
            subject=USER_ANALYST_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert analyst.status_code == 200
    get_settings.cache_clear()
