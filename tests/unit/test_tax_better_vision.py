from decimal import Decimal

import pytest

from sirta_api.domain.tax_better import receive_lines, support_catalog, vision_from_stored


def test_support_catalog_names_detran_and_venda_pj_without_amounts():
    catalog = support_catalog()
    venda = next(item for item in catalog["fgos"] if item["label"] == "VENDA PJ")
    assert venda["tax"] == "ICMS"
    assert venda["organ"] == "DETRAN"
    assert "DETRAN" in {item["code"] for item in catalog["organs"]}
    assert {item["code"] for item in catalog["taxes"]} == {
        "ICMS",
        "ISS",
        "IPTU",
        "IPVA",
        "ITBI",
        "ITCMD",
    }
    assert "4000000" not in str(catalog)


def test_vision_sums_each_measure_and_splits_on_every_variable():
    vision = receive_lines(
        [
                _line(cidade="Brasília", operationValue=Decimal("100"), malhaTax=Decimal("4")),
                _line(cidade="Brasília", operationValue=Decimal("50"), malhaTax=Decimal("1")),
                _line(cidade="Taguatinga", operationValue=Decimal("7"), malhaTax=Decimal("2")),
        ]
    )
    assert vision["createsTaxCredit"] is False
    by_city = {row["variables"]["cidade"]: row for row in vision["rows"]}
    assert by_city["Brasília"]["operacao"]["valor"] == Decimal("150")
    assert by_city["Brasília"]["malha"]["imposto"] == Decimal("5")
    assert by_city["Taguatinga"]["operacao"]["valor"] == Decimal("7")
    assert by_city["Brasília"]["approved"] is False


def test_missing_measure_stays_empty_instead_of_a_sample_total():
    vision = receive_lines([_line()])
    row = vision["rows"][0]
    assert row["operacao"] == {"valor": None, "baseCalculo": None, "imposto": None}
    assert row["malha"] == {"valor": None, "baseCalculo": None, "imposto": None}


def test_unknown_tax_or_blank_organ_is_refused():
    with pytest.raises(ValueError):
        receive_lines([_line(tax="ISS")])
    with pytest.raises(ValueError):
        receive_lines([_line(organ=" ")])


def test_stored_lines_keep_the_vision_without_credit():
    view = vision_from_stored(
        [
            _line(operationValue=Decimal("100")),
            _line(operationValue=Decimal("50"), malhaTax=Decimal("4")),
        ]
    )
    assert view["createsTaxCredit"] is False
    assert view["approvedExport"] is False
    assert view["emptyReason"] is None
    assert view["rows"][0]["approved"] is False
    assert view["rows"][0]["operacao"]["valor"] == "150"
    assert view["rows"][0]["operacao"]["baseCalculo"] is None
    assert view["rows"][0]["malha"]["imposto"] == "4"
    assert "4000000" not in str(view)


def test_empty_store_states_why_the_vision_is_blank():
    view = vision_from_stored([])
    assert view["createsTaxCredit"] is False
    assert view["rows"] == []
    assert view["emptyReason"] == "Ainda não há arquivo autorizado na visão."


def _line(**overrides):
    cidade = overrides.pop("cidade", "Brasília")
    payload = {
        "organ": "DETRAN",
        "tax": "ICMS",
        "fgo": "VENDA PJ",
        "variables": {"cidade": cidade},
        "operationValue": None,
        "operationBase": None,
        "operationTax": None,
        "malhaValue": None,
        "malhaBase": None,
        "malhaTax": None,
    }
    payload.update(overrides)
    return payload
