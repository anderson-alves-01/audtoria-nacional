"""Load the reliability registry and enforce it before an indicator feeds a calculation."""

from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
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
    "sped_transferencias_por_direcao",
    "sped_quantidade_uf_ano",
    "sped_quantidade_nacional_cfop_mes",
    "sped_valor_nacional_cfop_mes",
    "simulador_imposto_apurado_dados_publicos",
)


RATE_INDICATORS = ("icms_aliquota_ac", "icms_aliquota_demais_uf", "itcd_itbi_iss_aliquotas")


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


def authorize_fiscal_use(session: Session, *, context: AccessContext, indicator_id: str) -> dict:
    """Decide whether an indicator may feed a fiscal calculation and audit the decision.

    The refusal is committed before the 409 is raised: the request fails, the audit event stays.
    Only a registered indicator id is written to the event, never free text from the URL.
    """
    registry = load_registry()
    route = (
        f"/v1/indicator-reliability/{indicator_id}/fiscal-use"
        if indicator_id in registry
        else "/v1/indicator-reliability/{indicator_id}/fiscal-use"
    )
    try:
        ensure_fiscal_use(indicator_id, registry)
    except ConflictError:
        record_audit(
            session,
            context=context,
            action="indicator.fiscal_use",
            route=route,
            outcome="denied",
            resource_type="indicator",
        )
        session.commit()
        raise
    record_audit(
        session,
        context=context,
        action="indicator.fiscal_use",
        route=route,
        outcome="allowed",
        resource_type="indicator",
    )
    return indicator_view(indicator_id, registry)


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
