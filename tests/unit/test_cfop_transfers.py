"""Transfer methodology: direction by CFOP, pending codes and no sum across directions."""

from __future__ import annotations

import pytest
from tests.helpers.sped_fixture import build_sped_workbook

from sirta_api.adapters.ingest.sped_xlsx import parse_sped_workbook
from sirta_api.domain.sped_operations import (
    CLASS_CONFIRMED,
    CLASS_EXCLUDED,
    CLASS_PENDING,
    DIRECTION_RECEIVED,
    DIRECTION_SENT,
    PENDING_NAMED_CFOPS,
    TRANSFER_RECEIVED_CFOPS,
    TRANSFER_SENT_CFOPS,
    SpedBaseRow,
    SpedWorkbook,
    assert_single_direction,
    classify_cfop,
    classify_cfop_sirta,
    reconcile,
)


@pytest.mark.parametrize("cfop", sorted(TRANSFER_RECEIVED_CFOPS))
def test_confirmed_inbound_transfers_are_received_and_never_purchases(cfop: str) -> None:
    result = classify_cfop_sirta(cfop)
    assert result.operation == "Transferências"
    assert result.direction == DIRECTION_RECEIVED
    assert result.status == CLASS_CONFIRMED
    # The workbook's published rule would call these Compras; SIRTA must not.
    assert classify_cfop(cfop) == "Compras"
    assert result.operation != "Compras"


@pytest.mark.parametrize("cfop", sorted(TRANSFER_SENT_CFOPS))
def test_confirmed_outbound_transfers_are_sent(cfop: str) -> None:
    result = classify_cfop_sirta(cfop)
    assert (result.operation, result.direction, result.status) == (
        "Transferências",
        DIRECTION_SENT,
        CLASS_CONFIRMED,
    )


@pytest.mark.parametrize("cfop", sorted(PENDING_NAMED_CFOPS))
def test_named_codes_are_pending_with_no_operation(cfop: str) -> None:
    result = classify_cfop_sirta(cfop)
    assert result.status == CLASS_PENDING
    assert result.operation is None and result.direction is None


@pytest.mark.parametrize(
    "cfop", ["1155", "1158", "2155", "2157", "5154", "5157", "5159", "6159", "5160", "5192", "6162"]
)
def test_codes_in_the_transfer_ranges_missing_from_the_official_table_stay_pending(
    cfop: str,
) -> None:
    result = classify_cfop_sirta(cfop)
    assert result.status == CLASS_PENDING
    assert result.operation is None


def test_ordinary_purchases_sales_and_exclusions_are_unchanged() -> None:
    assert classify_cfop_sirta("1102").operation == "Compras"
    assert classify_cfop_sirta("2403").operation == "Compras"
    assert classify_cfop_sirta("5102").operation == "Vendas"
    assert classify_cfop_sirta("5910").operation == "Doações / bonificações / brindes"
    assert classify_cfop_sirta("1353").operation == "Serviços Tomados"
    for aggregator in ("1150", "5100", "5150", "2250"):
        assert classify_cfop_sirta(aggregator).status == CLASS_EXCLUDED
    assert classify_cfop_sirta("9999").status == CLASS_EXCLUDED
    assert classify_cfop_sirta("1949").status == CLASS_EXCLUDED  # inbound outside the groups


def test_the_two_directions_are_never_summed() -> None:
    assert assert_single_direction([DIRECTION_SENT, DIRECTION_SENT, None]) == DIRECTION_SENT
    assert assert_single_direction([None, None]) is None
    with pytest.raises(ValueError, match="dupla contagem"):
        assert_single_direction([DIRECTION_RECEIVED, DIRECTION_SENT])


def test_reconciliation_reports_transfer_volume_outside_the_official_table() -> None:
    workbook = parse_sped_workbook(build_sped_workbook())
    clean = reconcile(workbook)
    assert clean.transfer_quantity > 0
    assert clean.transfer_unconfirmed_quantity == 0

    extra = SpedBaseRow("AC", "5159", "Transferências", 2021, 1000, None)
    mixed = SpedWorkbook(workbook.serie, [*workbook.base, extra], workbook.consolidated)
    report = reconcile(mixed)
    assert report.transfer_unconfirmed_quantity == 1000
    assert any("não lista como transferência" in message for message in report.warnings)
