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


def test_findings_endpoint_is_empty_technical_shell(api_client) -> None:
    response = api_client.get("/v1/findings", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["binding"] is False
    assert body["commandsDisabled"] is True
    assert body["createsTaxCredit"] is False
    assert body["legalCommandsEnabled"] is False
    assert body["items"] == []
    assert body["total"] == 0
    assert body["g5Status"] == "BLOCKED"


def test_tech_admin_cannot_read_findings(api_client) -> None:
    response = api_client.get(
        "/v1/findings",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
