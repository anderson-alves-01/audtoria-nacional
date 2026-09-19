from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
)


def _analyst() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_active_debt_panel_endpoint_is_empty_official_shell(api_client) -> None:
    response = api_client.get("/v1/active-debt", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["commandsDisabled"] is True
    assert body["inscriptionEnabled"] is False
    assert body["createsTaxCredit"] is False
    assert body["legalCommandsEnabled"] is False
    assert body["items"] == []
    assert body["queue"] == []
    assert body["credentialStatus"] == "CREDENTIAL_REQUIRED"
    assert body["g0Status"] == "BLOCKED"


def test_active_debt_inscription_is_rejected(api_client) -> None:
    response = api_client.post("/v1/active-debt", headers=_analyst(), json={})
    assert response.status_code == 409
    detail = str(response.json().get("detail", response.json()))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_active_debt_panel(api_client) -> None:
    response = api_client.get(
        "/v1/active-debt",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
