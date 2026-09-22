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


def test_ops_governance_endpoint(api_client) -> None:
    response = api_client.get("/v1/ops-governance", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["canDeploy"] is False
    assert body["canApprove"] is False
    assert body["g10Status"] == "BLOCKED"
    assert body["runbooksComplete"] is True
    assert body["terraformApplyAuthorized"] is False
    assert len(body["runbooks"]) >= 5


def test_tech_admin_cannot_read_ops_governance(api_client) -> None:
    response = api_client.get(
        "/v1/ops-governance",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
