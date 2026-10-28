from datetime import date
from decimal import Decimal

from sirta_api.domain.tax_rates import RateVersion, resolve_on, resolve_year


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


def test_flat_taxes_use_the_national_row_and_ignore_uf() -> None:
    itcd = RateVersion("ITCD", "BR", "UNICA", Decimal("6"), None, None, "PENDENTE")
    assert resolve_on([itcd], "ITCD", None, date(2024, 1, 1)).rate == Decimal("6")
    assert resolve_on([itcd], "ITCD", "SP", date(2024, 1, 1)).rate == Decimal("6")
    assert resolve_on([itcd], "ICMS", "SP", date(2024, 1, 1)).rate is None


def test_non_modal_kinds_are_not_used_as_the_modal_rate() -> None:
    specific = RateVersion("ICMS", "SP", "ESPECIFICA", Decimal("12"), None, None, "VALIDADO")
    assert resolve_on([specific], "ICMS", "SP", date(2024, 1, 1)).rate is None
