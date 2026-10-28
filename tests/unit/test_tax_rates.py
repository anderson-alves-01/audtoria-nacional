from datetime import date
from decimal import Decimal

from sirta_api.domain.tax_rates import (
    RateVersion,
    homologation_gaps,
    is_homologated,
    resolve_on,
    resolve_year,
)


def _ac(rate: str, start: date | None, end: date | None, status: str = "VALIDADO") -> RateVersion:
    return RateVersion("ICMS", "AC", "MODAL", Decimal(rate), start, end, status)


AC = [_ac("17", None, date(2023, 3, 31)), _ac("19", date(2023, 4, 1), None)]


def test_acre_rate_changes_on_april_first_2023() -> None:
    assert resolve_on(AC, "ICMS", "AC", date(2023, 3, 31)).rate == Decimal("17")
    assert resolve_on(AC, "ICMS", "AC", date(2023, 4, 1)).rate == Decimal("19")
    assert resolve_on(AC, "ICMS", "AC", date(2021, 6, 1)).rate == Decimal("17")
    assert resolve_on(AC, "ICMS", "AC", date(2025, 12, 31)).rate == Decimal("19")


def test_year_with_a_change_inside_has_no_single_rate() -> None:
    assert resolve_year(AC, "ICMS", "AC", 2022).rate == Decimal("17")
    mixed = resolve_year(AC, "ICMS", "AC", 2023)
    assert mixed.rate is None
    assert mixed.changed_within_year is True
    assert resolve_year(AC, "ICMS", "AC", 2024).rate == Decimal("19")


def test_revoked_is_never_used() -> None:
    versions = [_ac("19", date(2023, 4, 1), None, status="REVOGADO")]
    assert resolve_on(versions, "ICMS", "AC", date(2024, 1, 1)).rate is None


def test_pending_is_flagged_and_loses_to_validated() -> None:
    pending = RateVersion("ICMS", "SP", "MODAL", Decimal("18"), None, None, "PENDENTE")
    result = resolve_on([pending], "ICMS", "SP", date(2024, 5, 1))
    assert result.rate == Decimal("18")
    assert result.status == "PENDENTE"
    validated = RateVersion(
        "ICMS", "SP", "MODAL", Decimal("19"), date(2024, 1, 1), None, "VALIDADO"
    )
    assert resolve_on([pending, validated], "ICMS", "SP", date(2024, 5, 1)).status == "VALIDADO"
    assert resolve_on([pending, validated], "ICMS", "SP", date(2024, 5, 1)).rate == Decimal("19")


def test_unknown_uf_or_missing_uf_returns_no_rate() -> None:
    assert resolve_on(AC, "ICMS", "SP", date(2024, 1, 1)).rate is None
    assert resolve_on(AC, "ICMS", None, date(2024, 1, 1)).rate is None
    assert resolve_year(AC, "ICMS", "SP", 2024).rate is None


def _sim(tax: str, rate: str) -> RateVersion:
    return RateVersion(
        tax, "BR", "UNICA", Decimal(rate), None, None, "PENDENTE", jurisdiction_level="SIMULACAO"
    )


def test_flat_taxes_use_the_simulation_row_and_label_it_as_such() -> None:
    itcd = _sim("ITCD", "6")
    first = resolve_on([itcd], "ITCD", None, date(2024, 1, 1))
    assert first.rate == Decimal("6")
    assert first.is_simulation is True
    assert resolve_on([itcd], "ITCD", "SP", date(2024, 1, 1)).rate == Decimal("6")
    assert resolve_on([itcd], "ICMS", "SP", date(2024, 1, 1)).rate is None


def test_a_real_state_rate_beats_the_simulation_parameter() -> None:
    sim = _sim("ITCD", "6")
    state = RateVersion("ITCD", "SP", "UNICA", Decimal("4"), date(2024, 1, 1), None, "VALIDADO")
    result = resolve_on([sim, state], "ITCD", "SP", date(2024, 6, 1))
    assert result.rate == Decimal("4")
    assert result.is_simulation is False
    assert resolve_on([sim, state], "ITCD", "RJ", date(2024, 6, 1)).is_simulation is True


def test_municipal_taxes_never_match_by_uf_alone() -> None:
    by_uf = RateVersion("ITBI", "SP", "UNICA", Decimal("2"), None, None, "VALIDADO")
    assert resolve_on([by_uf], "ITBI", "SP", date(2024, 1, 1)).rate is None
    city = RateVersion(
        "ITBI",
        "SP",
        "UNICA",
        Decimal("3"),
        None,
        None,
        "VALIDADO",
        jurisdiction_level="MUNICIPIO",
        municipality_ibge_code="3550308",
    )
    assert resolve_on([city], "ITBI", "SP", date(2024, 1, 1)).rate is None
    found = resolve_on([city], "ITBI", "SP", date(2024, 1, 1), municipality="3550308")
    assert found.rate == Decimal("3")
    assert resolve_on([city], "ITBI", "SP", date(2024, 1, 1), municipality="3304557").rate is None


def test_a_rate_tied_to_an_operation_needs_that_operation() -> None:
    iss = RateVersion(
        "ISS",
        "SP",
        "UNICA",
        Decimal("2"),
        None,
        None,
        "VALIDADO",
        jurisdiction_level="MUNICIPIO",
        municipality_ibge_code="3550308",
        operation_ref="LC116-7.02",
    )
    args = ("ISS", "SP", date(2024, 1, 1))
    assert resolve_on([iss], *args, municipality="3550308").rate is None
    assert resolve_on([iss], *args, municipality="3550308", operation="LC116-7.02").rate == 2


def test_non_modal_kinds_are_not_used_as_the_modal_rate() -> None:
    specific = RateVersion("ICMS", "SP", "ESPECIFICA", Decimal("12"), None, None, "VALIDADO")
    assert resolve_on([specific], "ICMS", "SP", date(2024, 1, 1)).rate is None


FULL = {
    "status": "VALIDADO",
    "legal_basis": "LC 1/2020",
    "official_url": "https://legis.example.gov.br/lc1",
    "validated_by": "responsável",
    "valid_from": date(2023, 4, 1),
    "homologated_by": "revisor responsável",
}


def test_a_rate_is_homologated_only_with_every_requirement() -> None:
    assert homologation_gaps(**FULL) == []
    assert is_homologated(**FULL)
    expected = {
        "legal_basis": "fundamento legal",
        "official_url": "URL oficial da legislação",
        "validated_by": "responsável pela validação",
        "valid_from": "início da vigência",
        "homologated_by": "homologação pelo responsável",
    }
    for field, gap in expected.items():
        assert homologation_gaps(**{**FULL, field: None}) == [gap]
        assert not is_homologated(**{**FULL, field: None})
    assert homologation_gaps(**{**FULL, "legal_basis": "  "}) == ["fundamento legal"]


def test_pending_rate_read_from_an_image_is_never_homologated() -> None:
    image_only = {
        "status": "PENDENTE",
        "legal_basis": None,
        "official_url": None,
        "validated_by": None,
        "valid_from": None,
    }
    gaps = homologation_gaps(**image_only)
    assert gaps == [
        "validação jurídica",
        "fundamento legal",
        "URL oficial da legislação",
        "responsável pela validação",
        "início da vigência",
        "homologação pelo responsável",
    ]
    # Even with a legal basis typed in, PENDENTE and the missing URL keep it out.
    assert not is_homologated(**{**FULL, "status": "PENDENTE", "official_url": None})
    assert not is_homologated(**{**FULL, "status": "REVOGADO"})


def test_documentation_alone_does_not_homologate_the_acre_rate() -> None:
    # The Acre row after migration 0110: legal basis, URL, validator and start are all filled.
    documented = {**FULL, "homologated_by": None}
    assert homologation_gaps(**documented) == ["homologação pelo responsável"]
    assert not is_homologated(**documented)


def test_a_simulation_parameter_is_never_homologated() -> None:
    gaps = homologation_gaps(**FULL, jurisdiction_level="SIMULACAO")
    assert len(gaps) == 1 and gaps[0].startswith("alíquota da jurisdição")
