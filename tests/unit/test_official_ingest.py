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
    assert len(silver) == 2
    assert all(row["ibgeCode"].isdigit() and len(row["ibgeCode"]) == 7 for row in silver)
    assert "cnpj" not in silver[0]
    assert len(quarantined) == 1


def test_tesouro_dictionary_includes_fpm() -> None:
    body = Path("tests/fixtures/official-snapshots/tesouro-transferencias.json").read_bytes()
    silver, quarantined = parse_tesouro_transfer_types(body)
    assert quarantined == []
    names = {row["transferName"] for row in silver}
    assert "FPM" in names
    assert len(silver) == 18
