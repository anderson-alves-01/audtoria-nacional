"""Build citável chart/KPI payloads from official Gold (reference / published transfers only)."""

from __future__ import annotations

CHARTABLE_VALUE_KINDS = frozenset({"REFERENCE_QUANTITY", "TRANSFER_AMOUNT_AS_PUBLISHED"})
TOP_N = 10


def build_dashboard_visuals(
    *,
    items: list[dict],
    lines: list[dict] | None = None,
) -> dict:
    chartable = [
        item
        for item in items
        if item.get("valueKind") in CHARTABLE_VALUE_KINDS
        and item.get("sourceId") != "COVERAGE-DIVERGENCE"
    ]
    kpis = _build_kpis(chartable)
    charts = _build_charts(chartable, lines or [])
    return {"kpis": kpis, "charts": charts}


def _evidence_ids(item: dict) -> list[str]:
    ids: list[str] = []
    gold_id = item.get("goldId") or item.get("evidenceId")
    if gold_id:
        ids.append(str(gold_id))
    return ids


def _build_kpis(items: list[dict]) -> list[dict]:
    kpis: list[dict] = []
    for item in items:
        evidence = _evidence_ids(item)
        if item.get("numericTotal") is not None:
            unit = "BRL" if item.get("financial") else "UNIT"
            kpis.append(
                {
                    "id": f"kpi-total-{item['sourceId']}",
                    "label": item.get("indicator") or item["sourceId"],
                    "value": float(item["numericTotal"]),
                    "unit": unit,
                    "valueKind": item["valueKind"],
                    "sourceId": item["sourceId"],
                    "evidenceId": evidence[0] if evidence else None,
                }
            )
        if item.get("coverageCount") is not None:
            kpis.append(
                {
                    "id": f"kpi-coverage-{item['sourceId']}",
                    "label": f"Cobertura {item['sourceId']}",
                    "value": int(item["coverageCount"]),
                    "unit": "COUNT",
                    "valueKind": item["valueKind"],
                    "sourceId": item["sourceId"],
                    "evidenceId": evidence[0] if evidence else None,
                }
            )
    return kpis


def _build_charts(items: list[dict], lines: list[dict]) -> list[dict]:
    charts: list[dict] = []
    if items:
        coverage_points = [
            {
                "x": item["sourceId"],
                "y": float(item.get("coverageCount") or 0),
            }
            for item in items
        ]
        evidence: list[str] = []
        for item in items:
            evidence.extend(_evidence_ids(item))
        charts.append(
            {
                "id": "coverage-by-source",
                "title": "Cobertura por fonte oficial",
                "type": "bar",
                "unit": "COUNT",
                "valueKind": "REFERENCE_QUANTITY",
                "series": [{"name": "Cobertura", "points": coverage_points}],
                "evidenceIds": list(dict.fromkeys(evidence)),
            }
        )
        total_points = [
            {
                "x": item.get("competence") or item["sourceId"],
                "y": float(item["numericTotal"]),
            }
            for item in items
            if item.get("numericTotal") is not None
        ]
        if total_points:
            charts.append(
                {
                    "id": "total-by-competence",
                    "title": "Total publicado por competência",
                    "type": "bar",
                    "unit": "MIXED",
                    "valueKind": "REFERENCE_QUANTITY",
                    "series": [{"name": "Total publicado", "points": total_points}],
                    "evidenceIds": list(dict.fromkeys(evidence)),
                }
            )

    chartable_sources = {item["sourceId"] for item in items}
    scoped_lines = [
        line
        for line in lines
        if line.get("sourceId") in chartable_sources and line.get("value") is not None
    ]
    if scoped_lines:
        by_ibge: dict[str, float] = {}
        line_evidence: list[str] = []
        for line in scoped_lines:
            code = line.get("ibgeCode") or "SEM-IBGE"
            by_ibge[code] = by_ibge.get(code, 0.0) + float(line["value"])
            line_id = line.get("id") or line.get("silverRowId")
            if line_id:
                line_evidence.append(str(line_id))
        ranked = sorted(by_ibge.items(), key=lambda pair: pair[1], reverse=True)[:TOP_N]
        charts.append(
            {
                "id": "top-municipalities",
                "title": f"Top {TOP_N} municípios (valores publicados)",
                "type": "bar",
                "unit": "MIXED",
                "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
                "series": [
                    {
                        "name": "Valor publicado",
                        "points": [{"x": code, "y": value} for code, value in ranked],
                    }
                ],
                "evidenceIds": list(dict.fromkeys(line_evidence))[:50],
            }
        )
    return charts
