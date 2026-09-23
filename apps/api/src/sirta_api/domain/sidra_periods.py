"""Select one official SIDRA year without replacing the years already published."""

from __future__ import annotations

import copy
import re

_YEAR = re.compile(r"\d{4}")


def sidra_comparison_periods(catalog: dict) -> list[str]:
    if str(catalog.get("connector") or "") != "ibge_sidra_series":
        return []
    raw = (catalog.get("parameters") or {}).get("comparison_periodos") or []
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if _YEAR.fullmatch(str(item))]


def catalog_for_sidra_period(catalog: dict, period: str) -> dict:
    """Copy a SIDRA catalog so the download and the Gold competence are that year."""
    year = str(period)
    cloned = copy.deepcopy(catalog)
    cloned["competence"] = year
    endpoint = str(cloned.get("endpoint") or "")
    cloned["endpoint"] = re.sub(r"/periodos/[^/?]+", f"/periodos/{year}", endpoint, count=1)
    parameters = dict(cloned.get("parameters") or {})
    parameters["periodo"] = year
    parameters.pop("comparison_periodos", None)
    cloned["parameters"] = parameters
    cloned["_period_expanded"] = True
    return cloned
