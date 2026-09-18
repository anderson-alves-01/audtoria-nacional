from sqlalchemy import select
from tests.helpers.tokens import auth_headers
from tests.helpers.validation import idempotency_headers, validation_payload

from sirta_api.adapters.db.models import CollectionCase, TaxCredit
from sirta_api.adapters.db.synthetic_ids import (
    CREDIT_ALPHA,
    CREDIT_BETA,
    EVIDENCE_ALPHA,
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
    USER_COLLECTOR_ALPHA,
    USER_VALIDATOR_ALPHA,
)


def _collector() -> dict[str, str]:
    return auth_headers(
        subject=USER_COLLECTOR_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _validator() -> dict[str, str]:
    return auth_headers(
        subject=USER_VALIDATOR_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _analyst() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _approve(api_client) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=idempotency_headers(_validator()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert response.status_code == 200


def test_identified_credit_cannot_start_collection(api_client, db_session) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/collection-cases",
        headers=idempotency_headers(_collector()),
    )
    assert response.status_code == 409
    credit = db_session.get(TaxCredit, CREDIT_ALPHA)
    assert credit is not None
    assert credit.collection_status == "NOT_STARTED"
    assert credit.version == 1
    cases = db_session.scalars(
        select(CollectionCase).where(CollectionCase.credit_id == CREDIT_ALPHA)
    ).all()
    assert cases == []


def test_validated_credit_starts_collection_with_sla(api_client, db_session) -> None:
    _approve(api_client)
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/collection-cases",
        headers=idempotency_headers(_collector()),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ADMINISTRATIVE"
    assert body["timeline"]
    assert body["slaDueAt"]
    credit = db_session.get(TaxCredit, CREDIT_ALPHA)
    assert credit is not None
    assert credit.collection_status == "ADMINISTRATIVE"
    assert credit.validation_status == "VALIDATED"


def test_analyst_cannot_start_collection(api_client) -> None:
    _approve(api_client)
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/collection-cases",
        headers=idempotency_headers(_analyst()),
    )
    assert response.status_code == 403


def test_suspended_validated_credit_cannot_be_collected(api_client) -> None:
    created = api_client.post(
        "/v1/tax-credits",
        headers=_analyst(),
        json={
            "tenantId": str(TENANT_ALPHA),
            "territoryId": str(TERRITORY_ALPHA_CENTRO),
            "purposeId": str(PURPOSE_ALPHA_ACTIVE),
            "taxpayerId": str(CREDIT_ALPHA),
            "taxType": "ISS",
            "competence": "2026-04",
            "sourceId": "synthetic-ledger",
            "principalAmount": 20,
            "calculationMemory": "base 200 * aliquota 0.10 = 20",
            "enforceabilityStatus": "SUSPENDED",
            "evidenceIds": [str(EVIDENCE_ALPHA)],
        },
    )
    assert created.status_code == 201
    credit_id = created.json()["id"]
    approved = api_client.post(
        f"/v1/tax-credits/{credit_id}/validations",
        headers=idempotency_headers(_validator()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert approved.status_code == 200
    collected = api_client.post(
        f"/v1/tax-credits/{credit_id}/collection-cases",
        headers=idempotency_headers(_collector()),
    )
    assert collected.status_code == 409
    assert collected.json()["status"] == 409


def test_cross_tenant_collection_is_hidden(api_client) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_BETA}/collection-cases",
        headers=idempotency_headers(_collector()),
    )
    assert response.status_code == 404
