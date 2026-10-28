"""O catálogo de municípios do Simulador é dado público de referência e precisa ser consistente."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "apps" / "web" / "public" / "ibge-municipios.json"
EVIDENCE = ROOT / "evidence" / "ops" / "ibge-municipios-20261028.txt"


def _document() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_catalog_covers_the_27_ufs_with_unique_seven_digit_codes() -> None:
    document = _document()
    cities = document["municipios"]
    assert document["total"] == len(cities) > 5500
    assert len({city["uf"] for city in cities}) == 27
    codes = [city["ibge"] for city in cities]
    assert len(set(codes)) == len(codes)
    assert all(re.fullmatch(r"\d{7}", code) for code in codes)


def test_catalog_holds_no_fiscal_data() -> None:
    document = _document()
    assert set(document["municipios"][0]) == {"uf", "ibge", "nome"}
    assert "aliquota" not in CATALOG.read_text(encoding="utf-8").lower()


def test_catalog_checksum_matches_the_evidence() -> None:
    digest = hashlib.sha256(CATALOG.read_bytes()).hexdigest()
    assert f"sha256 do arquivo gravado: {digest}" in EVIDENCE.read_text(encoding="utf-8")
