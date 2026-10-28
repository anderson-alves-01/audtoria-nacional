import pytest
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
    assert all(row.homologated_by is None for row in rows)
    assert all(row.valid_from is None for row in pending)
    assert db_session.scalar(select(func.count()).select_from(TaxRateVersion)) == 2 + 26 + 3


def test_lists_acre_versions_with_legal_basis(api_client) -> None:
    response = api_client.get("/v1/tax-rates?tax=ICMS&uf=AC", headers=_headers())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["createsTaxCredit"] is False
    assert "PENDENTE não é validação jurídica" in body["notice"]
    rates = [(item["rate"], item["validFrom"], item["validTo"]) for item in body["items"]]
    assert (17.0, "2002-01-01", "2023-03-31") in rates
    assert (19.0, "2023-04-01", None) in rates
    assert all(item["status"] == "VALIDADO" for item in body["items"])
    assert "nº 422, de 26/12/2022" in body["items"][-1]["legalBasis"]


def test_resolves_by_date_and_keeps_pending_labelled(api_client) -> None:
    before = api_client.get("/v1/tax-rates?tax=ICMS&uf=AC&on=2023-03-31", headers=_headers()).json()
    after = api_client.get("/v1/tax-rates?tax=ICMS&uf=AC&on=2023-04-01", headers=_headers()).json()
    assert before["resolved"] == {
        "rate": 17.0,
        "status": "VALIDADO",
        "isSimulationParameter": False,
    }
    assert after["resolved"] == {"rate": 19.0, "status": "VALIDADO", "isSimulationParameter": False}
    sp = api_client.get("/v1/tax-rates?tax=ICMS&uf=SP&on=2024-01-01", headers=_headers()).json()
    assert sp["resolved"] == {"rate": 18.0, "status": "PENDENTE", "isSimulationParameter": False}
    itcd = api_client.get("/v1/tax-rates?tax=ITCD&on=2024-01-01", headers=_headers()).json()
    assert itcd["resolved"] == {"rate": 6.0, "status": "PENDENTE", "isSimulationParameter": True}


def test_rejects_invalid_filters_and_requires_a_session(api_client) -> None:
    assert api_client.get("/v1/tax-rates?tax=IPI", headers=_headers()).status_code == 422
    assert api_client.get("/v1/tax-rates?uf=XX", headers=_headers()).status_code == 422
    assert api_client.get("/v1/tax-rates?on=31-12-2023", headers=_headers()).status_code == 422
    assert api_client.get("/v1/tax-rates").status_code in (401, 403)


def test_no_seeded_rate_is_homologated_and_each_item_says_what_is_missing(api_client) -> None:
    body = api_client.get("/v1/tax-rates", headers=_headers()).json()
    assert len(body["items"]) == 2 + 26 + 3
    assert all(item["homologated"] is False for item in body["items"])
    acre = [i for i in body["items"] if i["tax"] == "ICMS" and i["uf"] == "AC"]
    assert acre and all(i["status"] == "VALIDADO" for i in acre)
    # Legal documentation is complete; only the human homologation is missing.
    assert all(i["homologationGaps"] == ["homologação pelo responsável"] for i in acre)
    assert all(i["officialUrl"] and i["homologatedBy"] is None for i in acre)
    image_only = next(i for i in body["items"] if i["tax"] == "ICMS" and i["uf"] == "SP")
    assert image_only["status"] == "PENDENTE"
    assert {"validação jurídica", "fundamento legal", "início da vigência"} <= set(
        image_only["homologationGaps"]
    )


def test_acre_rows_carry_the_official_pages_and_validity_but_are_not_homologated(
    db_session,
) -> None:
    rows = {
        row.rate: row
        for row in db_session.scalars(
            select(TaxRateVersion).where(TaxRateVersion.tax == "ICMS", TaxRateVersion.uf == "AC")
        )
    }
    nineteen, seventeen = rows[19], rows[17]
    assert str(nineteen.valid_from) == "2023-04-01"
    assert str(seventeen.valid_from) == "2002-01-01"
    assert str(seventeen.valid_to) == "2023-03-31"
    assert nineteen.official_url == "https://sefaz.ac.gov.br/2021/?p=11479"
    assert seventeen.official_url == "https://sefaz.ac.gov.br/2021/?p=12159"
    assert "55/1997" in nineteen.legal_basis and "422" in nineteen.legal_basis
    assert "100" in seventeen.legal_basis
    assert nineteen.homologated_by is None and seventeen.homologated_by is None
    assert nineteen.homologated_at is None


def test_flat_taxes_are_simulation_parameters_with_reference_limits(api_client) -> None:
    body = api_client.get("/v1/tax-rates", headers=_headers()).json()
    flat = {i["tax"]: i for i in body["items"] if i["tax"] in ("ITCD", "ITBI", "ISS")}
    assert set(flat) == {"ITCD", "ITBI", "ISS"}
    for item in flat.values():
        assert item["jurisdictionLevel"] == "SIMULACAO"
        assert item["isSimulationParameter"] is True
        assert item["status"] == "PENDENTE"
        assert item["homologated"] is False
        assert item["homologationGaps"][0].startswith("alíquota da jurisdição")
        assert "parâmetro de simulação" in item["note"].lower()
    assert (flat["ITCD"]["referenceMin"], flat["ITCD"]["referenceMax"]) == (None, 8.0)
    assert (flat["ISS"]["referenceMin"], flat["ISS"]["referenceMax"]) == (2.0, 5.0)
    assert (flat["ITBI"]["referenceMin"], flat["ITBI"]["referenceMax"]) == (None, None)
    assert {i["jurisdictionLevel"] for i in body["items"] if i["tax"] == "ICMS"} == {"UF"}


def _version(**overrides) -> TaxRateVersion:
    from datetime import UTC, datetime
    from decimal import Decimal
    from uuid import uuid4

    values = {
        "id": uuid4(),
        "tax": "ITBI",
        "uf": "SP",
        "rate_kind": "UNICA",
        "rate": Decimal("3"),
        "status": "PENDENTE",
        "jurisdiction_level": "MUNICIPIO",
        "municipality_ibge_code": "3550308",
        "created_at": datetime.now(UTC),
    }
    return TaxRateVersion(**{**values, **overrides})


def test_register_keeps_one_rate_per_municipality_and_operation(db_session) -> None:
    from decimal import Decimal

    db_session.add_all(
        [
            _version(),
            _version(municipality_ibge_code="3304557", rate=Decimal("2")),
            _version(operation_ref="LC116-7.02", rate=Decimal("2.5")),
        ]
    )
    db_session.flush()
    count = db_session.scalar(
        select(func.count()).select_from(TaxRateVersion).where(TaxRateVersion.tax == "ITBI")
    )
    assert count == 3 + 1  # three municipal rows plus the simulation parameter


def test_register_rejects_the_same_municipality_operation_and_start_twice(db_session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    db_session.add(_version())
    db_session.flush()
    db_session.add(_version())
    with pytest.raises(IntegrityError):
        db_session.flush()


@pytest.mark.parametrize(
    "overrides",
    [
        {
            "jurisdiction_level": "SIMULACAO",
            "status": "VALIDADO",
            "legal_basis": "x",
            "validated_by": "y",
        },
        {"municipality_ibge_code": None},
        {"homologated_by": "revisor", "status": "PENDENTE"},
        {"reference_min": 5, "reference_max": 2},
        {"jurisdiction_level": "NACIONAL"},
    ],
)
def test_register_constraints_fail_closed(db_session, overrides) -> None:
    from sqlalchemy.exc import IntegrityError

    db_session.add(_version(**overrides))
    with pytest.raises(IntegrityError):
        db_session.flush()
