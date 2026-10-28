from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from sirta_api.application.indicator_reliability import (
    SPED_INDICATORS,
    ensure_fiscal_use,
    indicator_view,
    load_registry,
    reliability_for,
)
from sirta_api.domain.errors import ConflictError
from sirta_api.domain.indicator_reliability import (
    RegistryError,
    ReliabilityLevel,
    can_display,
    can_publish_in_simulator,
    can_use_as_hypothesis,
    can_use_in_fiscal_calculation,
    level_of,
    parse_registry,
)

ROOT = Path(__file__).resolve().parents[2]


def _payload(**overrides):
    item = {
        "id": "x",
        "level": "NAO_CONFIAVEL",
        "reason": "motivo",
        "evidence": ["evidence/a.md"],
        "reviewed_at": date(2026, 10, 28),
    }
    item.update(overrides)
    return {"version": 1, "indicators": [item]}


def test_levels_decide_what_each_use_is_allowed() -> None:
    nao, exploratorio, conferido = (
        ReliabilityLevel.NAO_CONFIAVEL,
        ReliabilityLevel.EXPLORATORIO,
        ReliabilityLevel.CONFERIDO,
    )
    assert [can_use_in_fiscal_calculation(x) for x in (nao, exploratorio, conferido)] == [
        False,
        False,
        True,
    ]
    assert [can_publish_in_simulator(x) for x in (nao, exploratorio, conferido)] == [
        False,
        False,
        True,
    ]
    assert [can_use_as_hypothesis(x) for x in (nao, exploratorio, conferido)] == [
        False,
        True,
        True,
    ]
    assert all(can_display(x) for x in (nao, exploratorio, conferido))


def test_unregistered_indicator_fails_closed() -> None:
    registry = parse_registry(_payload())
    assert level_of(registry, "nao-existe") is ReliabilityLevel.NAO_CONFIAVEL
    with pytest.raises(ConflictError) as error:
        ensure_fiscal_use("nao-existe", registry)
    assert error.value.status == 409


def test_conferido_requires_who_when_and_evidence() -> None:
    for missing in ({"conferred_by": None}, {"conferred_at": None}, {"evidence": []}):
        data = {
            "level": "CONFERIDO",
            "conferred_by": "responsável",
            "conferred_at": date(2026, 10, 28),
        }
        data.update(missing)
        with pytest.raises(RegistryError):
            parse_registry(_payload(**data))
    ok = parse_registry(
        _payload(level="CONFERIDO", conferred_by="responsável", conferred_at=date(2026, 10, 28))
    )
    ensure_fiscal_use("x", ok)  # não levanta


def test_registry_rejects_unknown_level_duplicate_and_missing_reason() -> None:
    with pytest.raises(RegistryError):
        parse_registry(_payload(level="OTIMO"))
    with pytest.raises(RegistryError):
        parse_registry(_payload(reason=""))
    with pytest.raises(RegistryError):
        parse_registry({"indicators": [{"id": "a", "level": "NAO_CONFIAVEL", "reason": "r"}] * 2})
    with pytest.raises(RegistryError):
        parse_registry({})


def test_shipped_registry_has_no_conferido_and_blocks_every_sped_indicator() -> None:
    registry = load_registry()
    assert registry, "registro vazio"
    assert not [i.id for i in registry.values() if i.level is ReliabilityLevel.CONFERIDO]
    for indicator_id in SPED_INDICATORS:
        assert indicator_id in registry, indicator_id
        with pytest.raises(ConflictError):
            ensure_fiscal_use(indicator_id, registry)
        view = indicator_view(indicator_id, registry)
        assert view["usableForFiscalCalculation"] is False
        assert view["publishableInSimulator"] is False


def test_the_value_and_compras_indicators_are_nao_confiavel() -> None:
    registry = load_registry()
    for indicator_id in (
        "sped_quantidade_uf_cfop_ano",
        "sped_compras_uf",
        "sped_valor_estimado_uf_cfop_ano",
        "sped_valor_estimado_operacao",
        "sped_transferencias_por_direcao",
        "simulador_imposto_apurado_dados_publicos",
    ):
        assert registry[indicator_id].level is ReliabilityLevel.NAO_CONFIAVEL, indicator_id
        assert indicator_view(indicator_id, registry)["usableAsHypothesis"] is False


def test_rates_are_never_conferido_just_because_an_image_listed_them() -> None:
    registry = load_registry()
    for indicator_id in ("icms_aliquota_ac", "icms_aliquota_demais_uf", "itcd_itbi_iss_aliquotas"):
        assert registry[indicator_id].level is ReliabilityLevel.EXPLORATORIO


def test_every_evidence_path_in_the_registry_exists() -> None:
    for indicator in load_registry().values():
        for path in indicator.evidence:
            assert (ROOT / path).exists(), f"{indicator.id}: {path}"


def test_reliability_block_lists_levels_and_indicators() -> None:
    block = reliability_for()
    assert block["levels"] == ["NAO_CONFIAVEL", "EXPLORATORIO", "CONFERIDO"]
    assert [item["id"] for item in block["indicators"]] == list(SPED_INDICATORS)


def test_invalid_registry_file_makes_loading_fail(tmp_path: Path) -> None:
    broken = tmp_path / "r.yaml"
    broken.write_text(yaml.safe_dump({"indicators": [{"id": "a", "level": "CONFERIDO"}]}))
    with pytest.raises(RegistryError):
        load_registry(broken)
