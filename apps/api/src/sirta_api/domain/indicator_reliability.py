"""Reliability levels of indicators and what each level allows.

Fail closed: an indicator that is not registered is NAO_CONFIAVEL. Only CONFERIDO can feed a
fiscal calculation or be published as public data in the Simulador. EXPLORATORIO can be shown with
a warning and can feed a hypothesis that the user labels as such. NAO_CONFIAVEL can be shown only
on the reference screens, with a warning, and never feeds a calculation or the Simulador.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any


class ReliabilityLevel(StrEnum):
    NAO_CONFIAVEL = "NAO_CONFIAVEL"
    EXPLORATORIO = "EXPLORATORIO"
    CONFERIDO = "CONFERIDO"


class RegistryError(ValueError):
    """The reliability registry is malformed. Loading fails instead of guessing a level."""


@dataclass(frozen=True)
class Indicator:
    id: str
    label: str
    level: ReliabilityLevel
    reason: str
    evidence: tuple[str, ...]
    reviewed_at: date | None
    conferred_by: str | None = None
    conferred_at: date | None = None


def can_display(level: ReliabilityLevel) -> bool:
    """Reference screens may show any level, always with the level and reason visible."""
    return True


def can_use_as_hypothesis(level: ReliabilityLevel) -> bool:
    """A user-labelled hypothesis may use a value that is at least EXPLORATORIO."""
    return level in (ReliabilityLevel.EXPLORATORIO, ReliabilityLevel.CONFERIDO)


def can_use_in_fiscal_calculation(level: ReliabilityLevel) -> bool:
    return level is ReliabilityLevel.CONFERIDO


def can_publish_in_simulator(level: ReliabilityLevel) -> bool:
    """Public data shown or compared in the Simulador requires a CONFERIDO indicator."""
    return level is ReliabilityLevel.CONFERIDO


def _as_date(value: Any, field: str, indicator_id: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    raise RegistryError(f"{indicator_id}: {field} deve ser uma data")


def parse_registry(payload: Any) -> dict[str, Indicator]:
    """Validate the YAML payload and return the indicators by id."""
    if not isinstance(payload, dict) or not isinstance(payload.get("indicators"), list):
        raise RegistryError("registro de confiabilidade inválido: falta a lista indicators")
    registry: dict[str, Indicator] = {}
    for raw in payload["indicators"]:
        if not isinstance(raw, dict):
            raise RegistryError("indicador inválido: esperado um objeto")
        indicator_id = str(raw.get("id") or "").strip()
        if not indicator_id:
            raise RegistryError("indicador sem id")
        if indicator_id in registry:
            raise RegistryError(f"indicador repetido: {indicator_id}")
        try:
            level = ReliabilityLevel(str(raw.get("level")))
        except ValueError as error:
            raise RegistryError(
                f"{indicator_id}: nível desconhecido {raw.get('level')!r}"
            ) from error
        reason = str(raw.get("reason") or "").strip()
        if not reason:
            raise RegistryError(f"{indicator_id}: falta o motivo")
        evidence_raw = raw.get("evidence") or []
        if not isinstance(evidence_raw, list):
            raise RegistryError(f"{indicator_id}: evidence deve ser uma lista")
        evidence = tuple(str(item) for item in evidence_raw if str(item).strip())
        conferred_by = str(raw["conferred_by"]).strip() if raw.get("conferred_by") else None
        conferred_at = _as_date(raw.get("conferred_at"), "conferred_at", indicator_id)
        if level is ReliabilityLevel.CONFERIDO and not (conferred_by and conferred_at and evidence):
            raise RegistryError(
                f"{indicator_id}: CONFERIDO exige conferred_by, conferred_at e uma evidência"
            )
        registry[indicator_id] = Indicator(
            id=indicator_id,
            label=str(raw.get("label") or indicator_id),
            level=level,
            reason=reason,
            evidence=evidence,
            reviewed_at=_as_date(raw.get("reviewed_at"), "reviewed_at", indicator_id),
            conferred_by=conferred_by,
            conferred_at=conferred_at,
        )
    return registry


def level_of(registry: dict[str, Indicator], indicator_id: str) -> ReliabilityLevel:
    """Unregistered indicators are NAO_CONFIAVEL."""
    indicator = registry.get(indicator_id)
    return indicator.level if indicator else ReliabilityLevel.NAO_CONFIAVEL
