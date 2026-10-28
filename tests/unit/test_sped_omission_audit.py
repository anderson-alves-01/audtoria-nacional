from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location(
        "sped_omission_audit", ROOT / "tools" / "ops" / "sped-omission-audit.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_assign_rule_follows_the_published_exclusions() -> None:
    mod = _load()
    assert mod.assign_rule("5100") == mod.AGREGADOR
    assert mod.assign_rule("1250") == mod.AGREGADOR
    assert mod.assign_rule("1949") == mod.ENTRADA_FORA
    assert mod.assign_rule("2556") == mod.ENTRADA_FORA
    assert mod.assign_rule("1152") == mod.SEM_REGRA
    assert mod.assign_rule("2159") == mod.SEM_REGRA


def test_audit_splits_legitimate_from_improper_and_keeps_the_invariant() -> None:
    mod = _load()
    history = {
        ("SP", "1152", 2024): (100, 1),  # Compras pela regra, ausente: indevida
        ("SP", "5102", 2024): (500, 1),  # presente na base: nao entra
        ("SP", "5100", 2024): (7, 1),  # agregador: legitima
        ("SP", "1949", 2024): (40, 1),  # entrada fora dos grupos: legitima_material
        ("SP", "1152", 2019): (900, 1),  # fora dos anos pedidos
        ("SP", "1153", 2024): (0, 0),  # quantidade zero
        ("SP", "1154", 2024): (None, None),
    }
    base = {("SP", "5102", 2024)}
    result = mod.audit(history, base)

    by_class = {item.cfop: item.klass for item in result}
    assert by_class == {"1152": "indevida", "5100": "legitima", "1949": "legitima_material"}
    assert {item.cfop: item.operation for item in result}["1152"] == "Compras"
    assert {item.cfop: item.operation for item in result}["1949"] == mod.FORA_DAS_CATEGORIAS
    legit = sum(1 for item in result if item.klass != "indevida")
    bad = sum(1 for item in result if item.klass == "indevida")
    assert legit + bad == len(result) == 3
    assert sum(item.quantity for item in result) == 147


def test_report_states_the_invariant_and_never_invents_a_share() -> None:
    mod = _load()
    result = mod.audit({("RO", "2152", 2024): (10, 1)}, set())
    text = mod.build_report(result, {2024: 10}, {}, {}, "20261028")
    assert "Invariante verificado" in text
    assert "SEM_REGRA_PUBLICADA" in text
    assert "—" in text  # sem Compras incluidas na UF, a razao e indefinida


def test_real_audit_matches_the_numbers_published_in_the_reconciliation_report() -> None:
    mod = _load()
    recon = mod._load_reconcile()
    if not (recon.HISTORY.is_file() and recon.WORKBOOK.is_file()):
        import pytest

        pytest.skip("originais oficiais ou planilha consolidada ausentes")
    history, _plain = recon.read_history()
    workbook = recon.parse_sped_workbook(recon.WORKBOOK.read_bytes())
    result = mod.audit(history, {(r.uf, r.cfop, r.year) for r in workbook.base})
    bad = [item for item in result if item.klass == "indevida"]
    assert len(result) == 22343
    assert len(bad) == 1041
    assert sum(item.quantity for item in bad) == 268317945
    assert {item.operation for item in bad} == {"Compras"}  # by the published rule, unchanged


def test_sirta_groups_split_confirmed_received_transfers_from_pending_codes() -> None:
    mod = _load()
    assert mod.sirta_group_of("1152") == mod.GROUP_RECEIVED
    assert mod.sirta_group_of("2154") == mod.GROUP_RECEIVED
    for pending in ("1159", "2159", "1190", "2170", "1155"):
        assert mod.sirta_group_of(pending) == mod.GROUP_PENDING
    assert mod.sirta_group_of("1102") == "Compras"
    result = mod.audit({("SP", "1152", 2024): (10, 1), ("SP", "2159", 2024): (30, 1)}, set())
    assert {item.cfop: item.sirta_group for item in result} == {
        "1152": mod.GROUP_RECEIVED,
        "2159": mod.GROUP_PENDING,
    }
    # The published-rule class and the counts do not move with the new methodology.
    assert {item.klass for item in result} == {"indevida"}


def test_report_section_10_never_adds_received_to_sent() -> None:
    mod = _load()
    result = mod.audit({("SP", "1152", 2024): (10, 1), ("SP", "2159", 2024): (30, 1)}, set())
    text = mod.build_report(result, {2024: 40}, {}, {}, "20261028", {"5159": 50, "5152": 150})
    assert (
        "## 10." in text and "TRANSFERENCIA_RECEBIDA" in text and "PENDENTE_CLASSIFICACAO" in text
    )
    assert "não são somadas" in text
    assert "## 11." in text
    assert "25,0%" in text  # 50 of 200 NF-e in Transferências are outside the official table
