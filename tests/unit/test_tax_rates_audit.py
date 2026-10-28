from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location(
        "tax_rates_audit", ROOT / "tools" / "ops" / "tax-rates-audit.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_no_seeded_rate_is_homologated() -> None:
    mod = _load()
    rows = mod.load_seed_rows()
    assert len(rows) == 2 + 26 + 3
    assert [row for row in rows if not mod.gaps_of(row)] == []


def test_image_only_icms_rates_miss_every_requirement() -> None:
    mod = _load()
    rows = [r for r in mod.load_seed_rows() if r["tax"] == "ICMS" and r["status"] == "PENDENTE"]
    assert len(rows) == 26
    for row in rows:
        assert set(mod.gaps_of(row)) == {
            "validação jurídica",
            "fundamento legal",
            "URL oficial da legislação",
            "responsável pela validação",
            "início da vigência",
        }


def test_acre_is_validated_but_still_lacks_the_official_url() -> None:
    mod = _load()
    acre = [r for r in mod.load_seed_rows() if r["uf"] == "AC"]
    assert {r["status"] for r in acre} == {"VALIDADO"}
    for row in acre:
        assert "URL oficial da legislação" in mod.gaps_of(row)
    assert "início da vigência" in mod.gaps_of(next(r for r in acre if r["rate"] == "17"))


def test_report_counts_zero_homologated() -> None:
    mod = _load()
    text = mod.build_report(mod.load_seed_rows(), "20261028")
    assert "Homologadas: **0**" in text
    assert "VALIDADO 2" in text and "PENDENTE 29" in text
