from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
)


def test_program_gates_remain_blocked_for_humans(api_client) -> None:
    response = api_client.get(
        "/v1/program-gates",
        headers=auth_headers(
            subject=USER_ANALYST_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["humanApprovalFabricated"] is False
    assert body["flags"]["cloud_apply"] is False
    g8 = next(item for item in body["gates"] if item["id"] == "G8")
    assert g8["homologated"] is False
    g0 = next(item for item in body["gates"] if item["id"] == "G0")
    assert g0["status"] == "BLOCKED"
    assert body["canApprove"] is False
    assert all(item["met"] is False for item in g0["checklist"])
    g1 = next(item for item in body["gates"] if item["id"] == "G1")
    assert g1["status"] == "BLOCKED"
    assert all(item["met"] is False for item in g1["checklist"])


def test_tech_admin_cannot_read_program_gates(api_client) -> None:
    response = api_client.get(
        "/v1/program-gates",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
