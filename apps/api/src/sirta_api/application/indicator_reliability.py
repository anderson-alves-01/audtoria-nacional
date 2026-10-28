"""Load the reliability registry and enforce it before an indicator feeds a calculation."""

from __future__ import annotations

from pathlib import Path

import yaml

from sirta_api.domain.errors import ConflictError
from sirta_api.domain.indicator_reliability import (
    Indicator,
    RegistryError,
    ReliabilityLevel,
    can_publish_in_simulator,
    can_use_as_hypothesis,
    can_use_in_fiscal_calculation,
    level_of,
    parse_registry,
)

REGISTRY_RELATIVE = Path("config/indicator-reliability.yaml")
UNREGISTERED_REASON = "Indicador não registrado. Tratado como NAO_CONFIAVEL."

# Indicators of the SPED reference data, in the order the screens list them.
SPED_INDICATORS = (
    "sped_quantidade_uf_cfop_ano",
    "sped_compras_uf",
    "sped_valor_estimado_uf_cfop_ano",
    "sped_valor_estimado_operacao",
    "sped_quantidade_uf_ano",
    "sped_quantidade_nacional_cfop_mes",
    "sped_valor_nacional_cfop_mes",
    "simulador_imposto_apurado_dados_publicos",
)


def registry_path() -> Path:
    here = Path(__file__).resolve()
    for parent in [Path.cwd(), *here.parents]:
        candidate = parent / REGISTRY_RELATIVE
        if candidate.is_file():
            return candidate
    raise RegistryError("registro de confiabilidade ausente: config/indicator-reliability.yaml")


def load_registry(path: Path | None = None) -> dict[str, Indicator]:
    source = path or registry_path()
    return parse_registry(yaml.safe_load(source.read_text(encoding="utf-8")))


def ensure_fiscal_use(indicator_id: str, registry: dict[str, Indicator] | None = None) -> None:
    """Raise 409 unless the indicator is CONFERIDO. Call it before any fiscal calculation."""
    level = level_of(registry if registry is not None else load_registry(), indicator_id)
    if not can_use_in_fiscal_calculation(level):
        raise ConflictError(
            f"O indicador {indicator_id} está {level.value} e não pode alimentar cálculo fiscal."
        )


def indicator_view(indicator_id: str, registry: dict[str, Indicator]) -> dict:
    indicator = registry.get(indicator_id)
    level = level_of(registry, indicator_id)
    return {
        "id": indicator_id,
        "label": indicator.label if indicator else indicator_id,
        "level": level.value,
        "reason": indicator.reason
        if indicator
        else "Indicador não registrado. Tratado como NAO_CONFIAVEL.",
        "evidence": list(indicator.evidence) if indicator else [],
        "usableForFiscalCalculation": can_use_in_fiscal_calculation(level),
        "publishableInSimulator": can_publish_in_simulator(level),
        "usableAsHypothesis": can_use_as_hypothesis(level),
    }


def reliability_for(indicator_ids: tuple[str, ...] = SPED_INDICATORS) -> dict:
    """Block added to API responses. An invalid registry makes the call fail (fail closed)."""
    registry = load_registry()
    return {
        "levels": [level.value for level in ReliabilityLevel],
        "indicators": [indicator_view(item, registry) for item in indicator_ids],
    }
