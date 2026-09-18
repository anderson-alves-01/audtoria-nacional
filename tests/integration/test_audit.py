from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)


def test_list_tax_credits_emits_audit_event(api_client) -> None:
    headers = auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    listed = api_client.get("/v1/tax-credits", headers=headers)
    assert listed.status_code == 200
    events = api_client.get("/v1/audit-events", headers=headers)
    assert events.status_code == 200
    actions = [item["action"] for item in events.json()["items"]]
    assert "tax_credit.list" in actions
    assert all("principalAmount" not in item for item in events.json()["items"])
