"""Roll published municipal money into one figure per state."""

from __future__ import annotations

from sirta_api.domain.dashboard_charts import is_statement_revenue_cell
from sirta_api.domain.executive_geography import UF_BY_CODE, assemble_geography

_UF_CODE = {uf: code for code, (uf, _name) in UF_BY_CODE.items()}

FINANCE_MAP_SOURCES = (
    "TESOURO-FPM-VALORES",
    "SICONFI-RREO",
    "SICONFI-DCA",
)

FINANCE_SOURCE_LABELS = {
    "TESOURO-FPM-VALORES": "FPM publicado",
    "SICONFI-RREO": "Receita corrente até o bimestre",
    "SICONFI-DCA": "Receitas brutas realizadas",
}

_PREFERRED_ACCOUNT = {
    "SICONFI-RREO": ("ReceitasCorrentes", "ReceitaCorrente"),
    "SICONFI-DCA": ("ReceitaOrcamentaria", "TotalReceitas"),
}


def aggregate_finance_geography(cells: list[dict]) -> dict:
    """One published municipal series per state.

    Forecast columns and a second parent account of the same statement stay
    out, so the color is a single realized figure. Missing states stay empty.
    """
    kept = [cell for cell in cells if _kept(cell)]
    return assemble_geography(
        _collapse(kept),
        allowed_sources=FINANCE_MAP_SOURCES,
        source_labels=FINANCE_SOURCE_LABELS,
    )


def _kept(cell: dict) -> bool:
    source_id = str(cell.get("sourceId") or "")
    if cell.get("total") is None:
        return False
    if source_id == "TESOURO-FPM-VALORES":
        return True
    if source_id not in _PREFERRED_ACCOUNT:
        return False
    account = str(cell.get("account") or "")
    column = str(cell.get("column") or "")
    if not is_statement_revenue_cell(source_id, account, column):
        return False
    folded = column.casefold()
    if source_id == "SICONFI-DCA":
        return folded == "receitas brutas realizadas"
    return "bimestre" in folded and "previs" not in folded and not folded.startswith("no ")


def _collapse(cells: list[dict]) -> list[dict]:
    buckets: dict[tuple[str, str, str], list[dict]] = {}
    for cell in cells:
        key = (
            str(cell.get("sourceId") or ""),
            str(cell.get("ufCode") or ""),
            str(cell.get("competence") or "")[:4],
        )
        buckets.setdefault(key, []).append(cell)
    groups = []
    for (source_id, uf_code, year), group in buckets.items():
        chosen = _preferred(source_id, group)
        if not chosen:
            continue
        groups.append(
            {
                "sourceId": source_id,
                "ufCode": uf_code,
                "label": FINANCE_SOURCE_LABELS[source_id],
                "unit": "BRL",
                "competence": year,
                "total": sum(float(cell["total"]) for cell in chosen),
                "municipalityCount": max(
                    int(cell.get("municipalityCount") or 0) for cell in chosen
                ),
            }
        )
    return groups


def finance_summary_records(view: dict) -> list[dict]:
    """One stored row per state, source and year. Empty states are omitted."""
    records = []
    for region in view.get("regions") or []:
        for state in region.get("states") or []:
            uf_code = _UF_CODE.get(str(state.get("uf") or ""))
            if not uf_code:
                continue
            for measure in state.get("measures") or []:
                records.append(
                    {
                        "sourceId": str(measure.get("sourceId") or ""),
                        "ufCode": uf_code,
                        "label": str(measure.get("label") or ""),
                        "unit": str(measure.get("unit") or "BRL"),
                        "competence": str(measure.get("competence") or "")[:4],
                        "total": float(measure["total"]),
                        "municipalityCount": int(measure.get("municipalityCount") or 0),
                    }
                )
    return records


def replace_summary_snapshot(_current: dict, incoming: list[dict]) -> dict:
    """The new rollup replaces the previous one. A second run does not append."""
    snapshot = {}
    for row in incoming:
        key = (row["sourceId"], row["ufCode"], row["competence"])
        snapshot[key] = row
    return snapshot


def view_from_summary(rows: list[dict]) -> dict:
    return assemble_geography(
        rows,
        allowed_sources=FINANCE_MAP_SOURCES,
        source_labels=FINANCE_SOURCE_LABELS,
    )


def _preferred(source_id: str, group: list[dict]) -> list[dict]:
    order = _PREFERRED_ACCOUNT.get(source_id)
    if order is None:
        return group
    for account in order:
        matches = [cell for cell in group if str(cell.get("account") or "") == account]
        if matches:
            return matches
    return []
