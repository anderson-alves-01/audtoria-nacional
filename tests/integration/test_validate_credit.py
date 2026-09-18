from sqlalchemy import select
from tests.helpers.tokens import auth_headers
from tests.helpers.validation import idempotency_headers, validation_payload

from sirta_api.adapters.db.models import CreditValidation, TaxCredit
from sirta_api.adapters.db.synthetic_ids import (
    CREDIT_ALPHA,
    CREDIT_BETA,
    EVIDENCE_ALPHA,
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
    USER_VALIDATOR_ALPHA,
)


def _validator_headers() -> dict[str, str]:
    return auth_headers(
        subject=USER_VALIDATOR_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _analyst_headers() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_validator_approves_identified_credit(api_client, db_session) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=idempotency_headers(_validator_headers()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["validationStatus"] == "VALIDATED"
    assert body["collectionStatus"] == "NOT_STARTED"
    assert body["version"] == 2
    credit = db_session.get(TaxCredit, CREDIT_ALPHA)
    assert credit is not None
    assert credit.validation_status == "VALIDATED"
    assert credit.version == 2
    rows = db_session.scalars(
        select(CreditValidation).where(CreditValidation.credit_id == CREDIT_ALPHA)
    ).all()
    assert len(rows) == 1


def test_incomplete_checklist_does_not_mutate_credit(api_client, db_session) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=idempotency_headers(_validator_headers()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)], complete=False),
    )
    assert response.status_code == 422
    credit = db_session.get(TaxCredit, CREDIT_ALPHA)
    assert credit is not None
    assert credit.validation_status == "IDENTIFIED"
    assert credit.version == 1
    rows = db_session.scalars(
        select(CreditValidation).where(CreditValidation.credit_id == CREDIT_ALPHA)
    ).all()
    assert rows == []


def test_second_approval_is_conflict_without_version_change(api_client, db_session) -> None:
    first = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=idempotency_headers(_validator_headers()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert first.status_code == 200
    second = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=idempotency_headers(_validator_headers()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert second.status_code == 409
    assert second.headers["content-type"].startswith("application/problem+json")
    credit = db_session.get(TaxCredit, CREDIT_ALPHA)
    assert credit is not None
    assert credit.validation_status == "VALIDATED"
    assert credit.version == 2
    rows = db_session.scalars(
        select(CreditValidation).where(CreditValidation.credit_id == CREDIT_ALPHA)
    ).all()
    assert len(rows) == 1


def test_idempotent_retry_replays_without_second_transition(api_client, db_session) -> None:
    headers = idempotency_headers(_validator_headers(), key="idem-repeat-alpha-01")
    payload = validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)])
    first = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations", headers=headers, json=payload
    )
    second = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations", headers=headers, json=payload
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    rows = db_session.scalars(
        select(CreditValidation).where(CreditValidation.credit_id == CREDIT_ALPHA)
    ).all()
    assert len(rows) == 1


def test_idempotency_key_conflict_on_different_payload(api_client) -> None:
    headers = idempotency_headers(_validator_headers(), key="idem-conflict-alpha-01")
    first = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=headers,
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert first.status_code == 200
    second = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=headers,
        json=validation_payload(
            decision="REJECT", evidence_ids=[str(EVIDENCE_ALPHA)], complete=False
        ),
    )
    assert second.status_code == 409


def test_analyst_cannot_validate(api_client) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
        headers=idempotency_headers(_analyst_headers()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert response.status_code == 403


def test_creator_cannot_validate_own_credit(api_client) -> None:
    created = api_client.post(
        "/v1/tax-credits",
        headers=_validator_headers(),
        json={
            "tenantId": str(TENANT_ALPHA),
            "territoryId": str(TERRITORY_ALPHA_CENTRO),
            "purposeId": str(PURPOSE_ALPHA_ACTIVE),
            "taxpayerId": str(CREDIT_ALPHA),
            "taxType": "ISS",
            "competence": "2026-03",
            "sourceId": "synthetic-ledger",
            "principalAmount": 10,
            "calculationMemory": "base 100 * aliquota 0.10 = 10",
            "enforceabilityStatus": "ENFORCEABLE",
            "evidenceIds": [str(EVIDENCE_ALPHA)],
        },
    )
    assert created.status_code == 201
    credit_id = created.json()["id"]
    response = api_client.post(
        f"/v1/tax-credits/{credit_id}/validations",
        headers=idempotency_headers(_validator_headers()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert response.status_code == 403
    detail = response.json()["detail"].lower()
    assert "creator" in detail or "segregat" in detail


def test_cross_tenant_validation_is_hidden(api_client) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_BETA}/validations",
        headers=idempotency_headers(_validator_headers()),
        json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
    )
    assert response.status_code == 404
