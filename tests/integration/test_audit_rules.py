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


def test_audit_rules_endpoint_is_non_binding(api_client) -> None:
    response = api_client.get("/v1/audit-rules", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["binding"] is False
    assert body["operational"] is False
    assert body["homologated"] is False
    assert body["createsTaxCredit"] is False
    assert body["taxPotentialAsCredit"] is False
    assert body["commandsDisabled"] is True
    assert body["catalogVersion"].startswith("audit-rules-")
    assert body["items"]
    assert all(item["binding"] is False for item in body["items"])
    assert all(item["status"] == "NON_BINDING" for item in body["items"])


def test_tech_admin_cannot_read_audit_rules(api_client) -> None:
    response = api_client.get(
        "/v1/audit-rules",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
