import pytest
from tests.helpers.sped_fixture import (
    CFOP_BY_OPERATION,
    OPERATIONS,
    UFS,
    YEARS,
    build_sped_workbook,
)

from sirta_api.adapters.ingest.catalog_loader import catalog_source
from sirta_api.adapters.ingest.sped_xlsx import SpedLayoutError, parse_sped_workbook
from sirta_api.domain.catalog import creates_tax_credit, ingest_allowed
from sirta_api.domain.sped_operations import (
    SPED_LAYOUT_VERSION,
    classify_cfop,
    reconcile,
)


def test_catalog_entry_is_public_open_reference_and_upload_only() -> None:
    entry = catalog_source("SPED-NFE-UF-CFOP")
    assert entry is not None
    assert entry["layout_version"] == SPED_LAYOUT_VERSION
    assert entry["access_classification"] == "PUBLIC_OPEN"
    assert entry["personal_data"] is False
    assert entry["connector"] == "uploaded_xlsx"
    assert "rateio" in entry["formula"].lower() or "estimat" in entry["formula"].lower()
    assert creates_tax_credit(entry["source_role"]) is False
    assert ingest_allowed(
        source_role=entry["source_role"],
        access_classification=entry["access_classification"],
        status=entry["status"],
        fixture_kind=entry["fixture_kind"],
    )


def test_parser_reads_series_base_and_consolidated_without_inventing_values() -> None:
    parsed = parse_sped_workbook(build_sped_workbook())
    assert len(parsed.serie) == len(UFS) * len(YEARS) * len(OPERATIONS)
    assert len(parsed.base) == len(UFS) * len(OPERATIONS) * len(YEARS)
    blank = next(
        row
        for row in parsed.serie
        if row.uf == "AC" and row.operation == "Serviços Prestados" and row.year == 2021
    )
    assert blank.quantity == 0
    assert blank.estimated_value is None
    first_base = parsed.base[0]
    assert first_base.cfop == CFOP_BY_OPERATION[first_base.operation]
    assert parsed.consolidated[("AC", "Serviços Prestados", "value")] is None


def test_parser_fails_closed_when_a_sheet_or_column_is_missing() -> None:
    with pytest.raises(SpedLayoutError, match="Base CFOP"):
        parse_sped_workbook(build_sped_workbook(drop_sheet="Base CFOP"))
    broken = list(
        ["Ano", "UF", "Operação", "Quantidade", "Valor UF estimado (R$)", "x", "y", "z", "w"]
    )
    with pytest.raises(SpedLayoutError, match="Quantidade de ocorrências"):
        parse_sped_workbook(build_sped_workbook(serie_header=broken))
    with pytest.raises(SpedLayoutError):
        parse_sped_workbook(b"not a workbook")


def test_reconciliation_passes_for_a_consistent_workbook() -> None:
    report = reconcile(parse_sped_workbook(build_sped_workbook()))
    assert report.ok, report.errors
    assert report.series_rows == 945
    assert report.base_rows == len(UFS) * len(OPERATIONS)
    assert report.errors == []


@pytest.mark.parametrize(
    ("kwargs", "needle"),
    [
        (
            {"mutate_serie": lambda rows: rows.pop()},
            "945",
        ),
        (
            {"mutate_serie": lambda rows: rows[0].__setitem__(1, "XX")},
            "UF",
        ),
        (
            {"mutate_serie": lambda rows: rows[0].__setitem__(0, 2019)},
            "ano",
        ),
        (
            {"mutate_serie": lambda rows: rows[0].__setitem__(3, -1)},
            "negativ",
        ),
        (
            {"mutate_base": lambda rows: rows[0].__setitem__(3, 999999)},
            "Base CFOP",
        ),
        (
            {"mutate_base": lambda rows: rows[0].__setitem__(1, "7999")},
            "CFOP",
        ),
        (
            {"mutate_consolidated": lambda totals: totals.__setitem__(("AC", "Compras", "qty"), 1)},
            "Consolidado",
        ),
    ],
)
def test_reconciliation_blocks_the_batch_on_divergence(kwargs: dict, needle: str) -> None:
    report = reconcile(parse_sped_workbook(build_sped_workbook(**kwargs)))
    assert not report.ok
    assert any(needle.lower() in message.lower() for message in report.errors), report.errors


def test_non_numeric_value_is_a_layout_error_not_a_zero() -> None:
    def break_value(rows: list) -> None:
        rows[0][4] = "abc"

    with pytest.raises(SpedLayoutError, match="não numérico"):
        parse_sped_workbook(build_sped_workbook(mutate_serie=break_value))


def test_cfop_classification_follows_the_published_prefix_rules() -> None:
    assert classify_cfop("1102") == "Compras"
    assert classify_cfop("2403") == "Compras"
    assert classify_cfop("5102") == "Vendas"
    assert classify_cfop("6404") == "Vendas"
    assert classify_cfop("5152") == "Transferências"
    assert classify_cfop("5910") == "Doações / bonificações / brindes"
    assert classify_cfop("5353") == "Serviços Prestados"
    assert classify_cfop("1353") == "Serviços Tomados"
    assert classify_cfop("5949") == "Outras Saídas"
    assert classify_cfop("5100") is None  # aggregators ending in 00 are excluded
    assert classify_cfop("5150") is None
