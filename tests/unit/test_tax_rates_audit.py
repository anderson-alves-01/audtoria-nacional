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
            "restrições e exceções registradas",
            "revisão humana registrada (responsável e data)",
            "homologação pelo responsável",
        }


def test_acre_19_has_the_primary_source_and_exceptions_but_misses_review_and_homologation() -> None:
    mod = _load()
    acre = [r for r in mod.load_seed_rows() if r["uf"] == "AC"]
    assert {r["status"] for r in acre} == {"VALIDADO"}
    nineteen = next(r for r in acre if r["rate"] == "19")
    seventeen = next(r for r in acre if r["rate"] == "17")
    assert nineteen["official_url"] == "https://www.legis.ac.gov.br/detalhar/5461"
    assert "sefaz.ac.gov.br" in nineteen["legal_basis"]
    assert "12% nas operações e prestações interestaduais" in nineteen["restrictions"]
    assert "lista completa de exceções não foi transcrita" in nineteen["restrictions"]
    assert mod.gaps_of(nineteen) == [
        "revisão humana registrada (responsável e data)",
        "homologação pelo responsável",
    ]
    # The 17% window has no listed exceptions: that gap stays visible instead of being filled in.
    assert seventeen["official_url"].startswith("https://sefaz.ac.gov.br/")
    assert mod.gaps_of(seventeen) == [
        "restrições e exceções registradas",
        "revisão humana registrada (responsável e data)",
        "homologação pelo responsável",
    ]
    assert str(seventeen["valid_from"]) == "2002-01-01"
    assert str(nineteen["valid_from"]) == "2023-04-01"


def test_flat_taxes_are_simulation_parameters_and_never_homologated() -> None:
    mod = _load()
    flat = [r for r in mod.load_seed_rows() if r["tax"] in ("ITCD", "ITBI", "ISS")]
    assert len(flat) == 3
    for row in flat:
        assert row["jurisdiction_level"] == "SIMULACAO"
        assert mod.gaps_of(row)[0].startswith("alíquota da jurisdição")


def test_report_counts_zero_homologated_and_states_the_new_requirement() -> None:
    mod = _load()
    text = mod.build_report(mod.load_seed_rows(), "20261028")
    assert "Homologadas: **0**" in text
    assert "VALIDADO 2" in text and "PENDENTE 29" in text
    assert "homologação pelo responsável" in text
    assert "Não existe alíquota única nacional" in text
