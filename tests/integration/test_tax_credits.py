from uuid import uuid4

from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    EVIDENCE_ALPHA,
    PURPOSE_ALPHA_ACTIVE,
    TAXPAYER_ALPHA,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)


def test_create_identified_credit_requires_calculation_memory(api_client) -> None:
    headers = auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    payload = {
        "tenantId": str(TENANT_ALPHA),
        "territoryId": str(TERRITORY_ALPHA_CENTRO),
        "purposeId": str(PURPOSE_ALPHA_ACTIVE),
        "taxpayerId": str(TAXPAYER_ALPHA),
        "taxType": "ISS",
        "competence": "2026-02",
        "sourceId": "synthetic-ledger",
        "principalAmount": 42,
        "calculationMemory": "base 420 * aliquota 0.10 = 42",
        "enforceabilityStatus": "ENFORCEABLE",
        "evidenceIds": [str(EVIDENCE_ALPHA)],
    }
    response = api_client.post("/v1/tax-credits", headers=headers, json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["validationStatus"] == "IDENTIFIED"
    assert body["collectionStatus"] == "NOT_STARTED"
    assert body["calculationMemory"]


def test_create_credit_rejects_tenant_mismatch(api_client) -> None:
    headers = auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    payload = {
        "tenantId": str(uuid4()),
        "territoryId": str(TERRITORY_ALPHA_CENTRO),
        "purposeId": str(PURPOSE_ALPHA_ACTIVE),
        "taxpayerId": str(TAXPAYER_ALPHA),
        "taxType": "ISS",
        "competence": "2026-02",
        "sourceId": "synthetic-ledger",
        "principalAmount": 42,
        "calculationMemory": "base 420 * aliquota 0.10 = 42",
        "enforceabilityStatus": "ENFORCEABLE",
        "evidenceIds": [str(EVIDENCE_ALPHA)],
    }
    response = api_client.post("/v1/tax-credits", headers=headers, json=payload)
    assert response.status_code == 403
