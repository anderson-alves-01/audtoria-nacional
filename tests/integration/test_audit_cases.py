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


def test_audit_cases_endpoint_is_empty_technical_shell(api_client) -> None:
    response = api_client.get("/v1/cases", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["binding"] is False
    assert body["commandsDisabled"] is True
    assert body["createsTaxCredit"] is False
    assert body["items"] == []
    assert body["g5Status"] == "BLOCKED"


def test_audit_cases_create_is_rejected(api_client) -> None:
    response = api_client.post("/v1/cases", headers=_analyst(), json={})
    assert response.status_code == 409
    body = response.json()
    detail = str(body.get("detail", body))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_audit_cases(api_client) -> None:
    response = api_client.get(
        "/v1/cases",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
