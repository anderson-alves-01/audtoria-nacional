from tests.helpers.tokens import auth_headers
from tests.helpers.validation import idempotency_headers, validation_payload

from sirta_api.adapters.db.synthetic_ids import (
    CREDIT_ALPHA,
    EVIDENCE_ALPHA,
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
    USER_VALIDATOR_ALPHA,
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


def test_validate_credit_emits_audit_without_rationale(api_client) -> None:
    headers = idempotency_headers(
        auth_headers(
            subject=USER_VALIDATOR_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        )
    )
    approved = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=headers,
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert approved.status_code == 200
    events = api_client.get("/v1/audit-events", headers=headers)
    assert events.status_code == 200
    actions = [item["action"] for item in events.json()["items"]]
    assert "tax_credit.validate" in actions
    serialized = str(events.json()["items"])
    assert "Synthetic validation decision" not in serialized
    assert "principalAmount" not in serialized
