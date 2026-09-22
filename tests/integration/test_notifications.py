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


def test_notifications_endpoint_is_empty_technical_shell(api_client) -> None:
    response = api_client.get("/v1/notifications", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["commandsDisabled"] is True
    assert body["sendEnabled"] is False
    assert body["createsTaxCredit"] is False
    assert body["items"] == []
    assert body["total"] == 0
    assert body["g5Status"] == "BLOCKED"


def test_notifications_send_is_rejected(api_client) -> None:
    response = api_client.post("/v1/notifications", headers=_analyst(), json={})
    assert response.status_code == 409
    body = response.json()
    detail = str(body.get("detail", body))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_notifications(api_client) -> None:
    response = api_client.get(
        "/v1/notifications",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
