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


def test_transfer_reconciliation_endpoint_is_empty_shell(api_client) -> None:
    response = api_client.get("/v1/transfer-reconciliation", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["commandsDisabled"] is True
    assert body["autoReconcileEnabled"] is False
    assert body["createsTaxCredit"] is False
    assert body["differenceIsOccurrenceOnly"] is True
    assert body["items"] == []
    assert body["differences"] == []
    assert body["total"] == 0
    assert body["g7Status"] == "LOCAL_GO_OFFICIAL_BLOCKED"


def test_transfer_reconciliation_command_is_rejected(api_client) -> None:
    response = api_client.post("/v1/transfer-reconciliation", headers=_analyst(), json={})
    assert response.status_code == 409
    detail = str(response.json().get("detail", response.json()))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_transfer_reconciliation(api_client) -> None:
    response = api_client.get(
        "/v1/transfer-reconciliation",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
