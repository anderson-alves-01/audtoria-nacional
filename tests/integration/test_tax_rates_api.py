from sqlalchemy import func, select
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.models import TaxRateVersion
from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)


def _headers() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_migration_seeds_only_acre_as_validated(db_session) -> None:
    rows = list(db_session.scalars(select(TaxRateVersion)))
    validated = [row for row in rows if row.status == "VALIDADO"]
    assert {(row.tax, row.uf) for row in validated} == {("ICMS", "AC")}
    assert all(row.legal_basis and row.validated_by for row in validated)
    pending = [row for row in rows if row.status == "PENDENTE"]
    assert len(pending) == 26 + 3
    assert all(row.legal_basis is None and row.official_url is None for row in pending)
    assert all(row.valid_from is None for row in pending)
    assert db_session.scalar(select(func.count()).select_from(TaxRateVersion)) == 2 + 26 + 3


def test_lists_acre_versions_with_legal_basis(api_client) -> None:
    response = api_client.get("/v1/tax-rates?tax=ICMS&uf=AC", headers=_headers())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["createsTaxCredit"] is False
    assert "PENDENTE não é validação jurídica" in body["notice"]
    rates = [(item["rate"], item["validFrom"], item["validTo"]) for item in body["items"]]
    assert (17.0, None, "2023-03-31") in rates
    assert (19.0, "2023-04-01", None) in rates
    assert all(item["status"] == "VALIDADO" for item in body["items"])
    assert "422/2022" in body["items"][-1]["legalBasis"]


def test_resolves_by_date_and_keeps_pending_labelled(api_client) -> None:
    before = api_client.get("/v1/tax-rates?tax=ICMS&uf=AC&on=2023-03-31", headers=_headers()).json()
    after = api_client.get("/v1/tax-rates?tax=ICMS&uf=AC&on=2023-04-01", headers=_headers()).json()
    assert before["resolved"] == {"rate": 17.0, "status": "VALIDADO"}
    assert after["resolved"] == {"rate": 19.0, "status": "VALIDADO"}
    sp = api_client.get("/v1/tax-rates?tax=ICMS&uf=SP&on=2024-01-01", headers=_headers()).json()
    assert sp["resolved"] == {"rate": 18.0, "status": "PENDENTE"}
    itcd = api_client.get("/v1/tax-rates?tax=ITCD&on=2024-01-01", headers=_headers()).json()
    assert itcd["resolved"] == {"rate": 6.0, "status": "PENDENTE"}


def test_rejects_invalid_filters_and_requires_a_session(api_client) -> None:
    assert api_client.get("/v1/tax-rates?tax=IPI", headers=_headers()).status_code == 422
    assert api_client.get("/v1/tax-rates?uf=XX", headers=_headers()).status_code == 422
    assert api_client.get("/v1/tax-rates?on=31-12-2023", headers=_headers()).status_code == 422
    assert api_client.get("/v1/tax-rates").status_code in (401, 403)
