from tests.helpers.tokens import auth_headers
from tests.helpers.validation import idempotency_headers, validation_payload

from sirta_api.adapters.db.synthetic_ids import (
    CREDIT_ALPHA,
    EVIDENCE_ALPHA,
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_COLLECTOR_ALPHA,
    USER_DEBT_ALPHA,
    USER_VALIDATOR_ALPHA,
)


def _headers(subject) -> dict[str, str]:
    return auth_headers(
        subject=subject,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _prepare_collected(api_client) -> None:
    assert (
        api_client.post(
            f"/v1/tax-credits/{CREDIT_ALPHA}/validations",
            headers=idempotency_headers(_headers(USER_VALIDATOR_ALPHA)),
            json=validation_payload(evidence_ids=[str(EVIDENCE_ALPHA)]),
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            f"/v1/tax-credits/{CREDIT_ALPHA}/collection-cases",
            headers=idempotency_headers(_headers(USER_COLLECTOR_ALPHA)),
        ).status_code
        == 201
    )


def test_payment_without_collection_is_blocked(api_client) -> None:
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/payments",
        headers=_headers(USER_COLLECTOR_ALPHA),
        json={"reconciliationRef": "bank-synth-01"},
    )
    assert response.status_code == 409


def test_reconciled_payment_after_collection(api_client) -> None:
    _prepare_collected(api_client)
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/payments",
        headers=_headers(USER_COLLECTOR_ALPHA),
        json={"reconciliationRef": "bank-synth-01"},
    )
    assert response.status_code == 200
    assert response.json()["paymentStatus"] == "PAID"


def test_active_debt_after_collection(api_client) -> None:
    _prepare_collected(api_client)
    response = api_client.post(
        f"/v1/tax-credits/{CREDIT_ALPHA}/active-debt-proposals",
        headers=_headers(USER_DEBT_ALPHA),
    )
    assert response.status_code == 200
    assert response.json()["collectionStatus"] == "ACTIVE_DEBT"
