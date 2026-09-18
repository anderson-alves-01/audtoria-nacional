from sqlalchemy import func, select
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.models import TaxCredit
from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)


def _analyst() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_transfer_occurrence_never_creates_tax_credit(api_client, db_session) -> None:
    before = db_session.scalar(select(func.count()).select_from(TaxCredit))
    response = api_client.post(
        "/v1/transfer-occurrences",
        headers=_analyst(),
        json={
            "transferType": "FPM",
            "competence": "2026-01",
            "officialSource": "synthetic-tesouro",
            "expectedAmount": 100,
            "receivedAmount": 90,
        },
    )
    assert response.status_code == 201
    assert response.json()["taxCreditCreated"] is False
    assert response.json()["classification"] == "OCCURRENCE_NOT_TAX_CREDIT"
    after = db_session.scalar(select(func.count()).select_from(TaxCredit))
    assert after == before


def test_transfer_without_competence_is_rejected(api_client) -> None:
    response = api_client.post(
        "/v1/transfer-occurrences",
        headers=_analyst(),
        json={
            "transferType": "FPM",
            "competence": "",
            "officialSource": "synthetic-tesouro",
            "receivedAmount": 1,
        },
    )
    assert response.status_code == 422
