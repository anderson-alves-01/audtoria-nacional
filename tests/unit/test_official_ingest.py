from pathlib import Path

from sirta_api.adapters.ingest.parsers import (
    parse_ibge_sidra_series,
    parse_siconfi_entes,
    parse_tesouro_transfer_types,
)


def test_ibge_snapshot_quarantines_invalid_municipality_code() -> None:
    body = Path("tests/fixtures/official-snapshots/ibge-6579.json").read_bytes()
    silver, quarantined = parse_ibge_sidra_series(body)
    assert len(silver) == 2
    assert {row["ibgeCode"] for row in silver} == {"3304557", "3550308"}
    assert silver[0]["value"] == 6731133
    assert len(quarantined) == 1
    assert quarantined[0][1] == "invalid IBGE municipality code"


def test_siconfi_snapshot_keeps_municipal_ibge_codes() -> None:
    body = Path("tests/fixtures/official-snapshots/siconfi-entes.json").read_bytes()
    silver, quarantined = parse_siconfi_entes(body)
    assert len(silver) == 28
    assert all(row["ibgeCode"].isdigit() and len(row["ibgeCode"]) == 7 for row in silver)
    assert {row["ibgeCode"] for row in silver} >= {
        "2100055",
        "2100154",
        "2103505",
        "2103554",
        "2400109",
        "2408102",
        "2600054",
        "2611606",
        "2900108",
        "2900702",
        "5000203",
        "5002704",
        "5200050",
        "5208707",
        "1100205",
        "1100122",
        "2300101",
        "2304400",
        "4300034",
        "4314902",
        "1200013",
        "1200054",
        "2200053",
        "2200103",
        "4104808",
        "4106902",
        "1501402",
        "1500800",
    }
    assert "cnpj" not in silver[0]
    assert len(quarantined) == 1


def test_tesouro_dictionary_includes_fpm() -> None:
    body = Path("tests/fixtures/official-snapshots/tesouro-transferencias.json").read_bytes()
    silver, quarantined = parse_tesouro_transfer_types(body)
    assert quarantined == []
    names = {row["transferName"] for row in silver}
    assert "FPM" in names
    assert len(silver) == 18
    assert all(row["unit"] == "tipo" for row in silver)
