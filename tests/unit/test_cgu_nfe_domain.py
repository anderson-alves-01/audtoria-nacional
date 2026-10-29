"""Pure rules of the CGU NF-e pipeline. Synthetic inputs only."""

from decimal import Decimal

import pytest
from tests.helpers.cgu_nfe_synthetic import ITEM_HEADER, NOTE_HEADER, access_key

from sirta_api.domain import cgu_nfe as d


def test_sixty_months_from_2021_01_to_2025_12() -> None:
    months = d.requested_months()
    assert len(months) == 60
    assert months[0] == "202101"
    assert months[-1] == "202512"
    assert len(set(months)) == 60


def test_month_url_and_file_names() -> None:
    assert d.month_url("202404").endswith("/saida/nfe/202404_NFe.zip")
    assert d.month_from_filename("C:/x/202404_NFe.zip") == "202404"
    assert d.month_from_filename("nfe_sem_mes.zip") is None
    assert d.month_from_filename("999999_NFe.zip") is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1234,56", Decimal("1234.56")),
        ("1.234,56", Decimal("1234.56")),
        ("0,5", Decimal("0.5")),
        ("12.5", Decimal("12.5")),
        ("-3,10", Decimal("-3.10")),
        ("  7  ", Decimal("7")),
        ("2,5000", Decimal("2.5000")),
    ],
)
def test_parse_decimal(text: str, expected: Decimal) -> None:
    value = d.parse_decimal(text)
    assert value == expected
    assert str(value) == str(expected)  # source precision survives


@pytest.mark.parametrize("text", [None, "", "   "])
def test_blank_is_none_never_zero(text) -> None:
    assert d.parse_decimal(text) is None
    assert d.to_cents(d.parse_decimal(text)) is None
    assert d.cents_to_text(None) == ""


@pytest.mark.parametrize("text", ["abc", "1.2.3", "1,2,3", "R$ 10", "1e5", "--1"])
def test_ambiguous_or_invalid_numbers_are_refused(text: str) -> None:
    with pytest.raises(d.ValueRefused):
        d.parse_decimal(text)


def test_to_cents_is_exact_and_never_rounds() -> None:
    assert d.to_cents(Decimal("1234.56")) == 123456
    assert d.to_cents(Decimal("0.1")) == 10
    assert d.to_cents(Decimal("181503493481.79")) == 18150349348179
    with pytest.raises(d.ValueRefused):
        d.to_cents(Decimal("10.005"))


def test_money_and_decimal_text_round_trip() -> None:
    assert d.cents_to_text(123456) == "1234,56"
    assert d.cents_to_text(-5) == "-0,05"
    assert d.decimal_to_text(Decimal("1E+3")) == "1000"
    assert d.decimal_to_text(Decimal("2.5000")) == "2,5000"


def test_header_normalization_ignores_case_accents_and_punctuation() -> None:
    assert d.normalize_header("  Município   EMITENTE ") == "MUNICIPIO EMITENTE"
    assert d.normalize_header("CPF/CNPJ Emitente") == "CPF CNPJ EMITENTE"
    assert d.normalize_header("\ufeffCHAVE DE ACESSO") == "CHAVE DE ACESSO"


def test_map_header_maps_known_fields_and_reports_unknown() -> None:
    mapping = d.map_header(d.KIND_NOTE, NOTE_HEADER)
    assert mapping.index["chave"] == 0
    assert mapping.index["valor_nota"] == NOTE_HEADER.index("VALOR NOTA FISCAL")
    assert "RAZÃO SOCIAL EMITENTE" in mapping.unknown
    assert mapping.width == len(NOTE_HEADER)


def test_map_header_fails_closed_when_a_required_column_is_missing() -> None:
    header = [h for h in ITEM_HEADER if h != "VALOR TOTAL"]
    with pytest.raises(d.SchemaError, match="valor_total"):
        d.map_header(d.KIND_ITEM, header)


def test_detect_kind_by_name_and_by_header() -> None:
    assert d.detect_kind("202401_NFe_NotaFiscalItem.csv", ["x"]) == d.KIND_ITEM
    assert d.detect_kind("202401_NFe_NotaFiscalEvento.csv", ["x"]) == d.KIND_EVENT
    assert d.detect_kind("202401_NFe_NotaFiscal.csv", ["x"]) == d.KIND_NOTE
    assert d.detect_kind("leiame.csv", ["a", "b"]) is None
    assert d.detect_kind("dados.csv", ["CÓDIGO NCM/SH"]) == d.KIND_ITEM


def test_access_key_shape_and_check_digit() -> None:
    key = access_key(7)
    assert d.is_access_key(key)
    assert d.access_key_dv_ok(key)
    wrong = key[:-1] + str((int(key[-1]) + 1) % 10)
    assert d.is_access_key(wrong)
    assert not d.access_key_dv_ok(wrong)
    assert not d.is_access_key(key[:-1])
    assert not d.is_access_key("A" * 44)


def test_identifiers_stay_text_with_leading_zeros() -> None:
    assert d.clean_identifier(" 01012100 ") == "01012100"
    assert d.clean_identifier(None) == ""


def test_digests_are_stable_and_distinguish_items() -> None:
    key = access_key(1)
    assert d.key_digest(key) == d.key_digest(key)
    assert d.item_digest(key, "1") != d.item_digest(key, "2")
    assert d.fingerprint(["a", "b"]) != d.fingerprint(["a", "c"])
    assert d.fingerprint(["a", "b"]) != d.fingerprint(["ab", ""])


def test_dates() -> None:
    assert d.month_of(d.parse_date("10/01/2024")) == "202401"
    assert d.month_of(d.parse_date("10/01/2024 13:45:00")) == "202401"
    assert d.month_of(d.parse_date("2024-02-29")) == "202402"
    assert d.parse_date("") is None
    with pytest.raises(d.ValueRefused):
        d.parse_date("31/02/2024")


@pytest.mark.parametrize(
    ("latest", "events", "expected"),
    [
        ("Cancelamento de NF-e", set(), d.SIT_CANCELLED),
        ("", {"Cancelamento de NF-e homologado"}, d.SIT_CANCELLED),
        ("Carta de Correção", {"Carta de Correção", "CANCELAMENTO"}, d.SIT_CANCELLED),
        ("Carta de Correção", {"Ciência da Operação"}, d.SIT_OTHER_EVENT),
        ("", set(), d.SIT_NO_EVENT),
        (None, set(), d.SIT_NO_EVENT),
    ],
)
def test_situation_comes_from_events_only(latest, events, expected) -> None:
    assert d.classify_situation(latest, events) == expected


def test_state_is_derived_from_recorded_facts() -> None:
    assert d.derive_state(listed=False) == d.STATE_NOT_LISTED
    assert d.derive_state(listed=True) == d.STATE_PENDING
    assert d.derive_state(listed=True, blocked=True) == d.STATE_BLOCKED
    assert d.derive_state(listed=True, blocked=True, invalid=True) == d.STATE_INVALID
    assert d.derive_state(listed=True, blocked=True, validated=True) == d.STATE_VALIDATED
    assert d.derive_state(listed=False, validated=True, processed=True) == d.STATE_DONE
    assert len(d.MONTH_STATES) == 6


def test_coverage_is_partial_until_every_requested_month_is_processed() -> None:
    requested = d.requested_months()
    assert d.coverage_of(requested, []) == ("AUSENTE", requested)
    one = ["202401"]
    kind, missing = d.coverage_of(requested, one)
    assert kind == "PARCIAL"
    assert "202401" not in missing
    assert len(missing) == 59
    assert d.coverage_of(requested, requested) == ("COMPLETO", [])


def test_roll_year_uf_keeps_cancelled_out_of_the_simulator_measure() -> None:
    items = [
        ("2024", "SP", d.SIT_NO_EVENT, 10, 1000),
        ("2024", "SP", d.SIT_CANCELLED, 2, 200),
        ("2024", "RJ", d.SIT_OTHER_EVENT, 5, 500),
    ]
    notes = [
        ("2024", "SP", d.SIT_NO_EVENT, 3, 900),
        ("2024", "SP", d.SIT_CANCELLED, 1, 100),
    ]
    rows = d.roll_year_uf(item_rows=items, note_rows=notes)
    sp = next(row for row in rows if row.uf == "SP")
    assert sp.itens == 10
    assert sp.valor_itens_cents == 1000
    assert sp.itens_bruto == 12
    assert sp.notas == 3
    assert sp.valor_notas_cents == 900
    payload = d.series_item(sp)
    assert payload["itens"] == 10
    assert payload["valorItens"] == "10.00"
    assert payload["itensCancelados"] == 2


def test_cents_to_decimal_text_is_exact() -> None:
    assert d.cents_to_decimal_text(1) == "0.01"
    assert d.cents_to_decimal_text(100) == "1.00"
    assert d.cents_to_decimal_text(12345) == "123.45"
