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


def test_municipal_uploads_endpoint_is_empty_shell(api_client) -> None:
    response = api_client.get("/v1/municipal-uploads", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["uploadEnabled"] is False
    assert body["quarantineRequired"] is True
    assert body["tenantScoped"] is True
    assert body["createsTaxCredit"] is False
    assert body["samplePresent"] is False
    assert body["items"] == []
    assert body["total"] == 0
    assert body["g0Status"] == "BLOCKED"
    assert body["institutionalStatus"] == "CREDENTIAL_REQUIRED"
    assert len(body["slots"]) == 6


def test_municipal_uploads_command_is_rejected(api_client) -> None:
    response = api_client.post("/v1/municipal-uploads", headers=_analyst(), json={})
    assert response.status_code == 409
    detail = str(response.json().get("detail", response.json()))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_municipal_uploads(api_client) -> None:
    response = api_client.get(
        "/v1/municipal-uploads",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
