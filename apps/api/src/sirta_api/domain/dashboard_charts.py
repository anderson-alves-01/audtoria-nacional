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
    scoped = lines or []
    kpis = _build_kpis(chartable, scoped)
    charts = _build_charts(chartable, scoped)
    return {"kpis": kpis, "charts": charts}


def separate_measures(items: list[dict], lines: list[dict]) -> None:
    """Attach per-variable figures when a source mixes measures. Leaves numericTotal intact."""
    for item in items:
        grouped = _groups(item, lines)
        if len(grouped) < 2:
            continue
        item["measures"] = [
            {
                "label": _measure_label(rows[0], item),
                "unit": str(rows[0].get("unit") or "UNIT"),
                "value": sum(float(row["value"]) for row in rows),
                "count": len(rows),
            }
            for rows in grouped.values()
        ]


def _evidence_ids(item: dict) -> list[str]:
    ids: list[str] = []
    gold_id = item.get("goldId") or item.get("evidenceId")
    if gold_id:
        ids.append(str(gold_id))
    return ids


def _payload(line: dict) -> dict:
    payload = line.get("payload")
    return payload if isinstance(payload, dict) else {}


def _measure_key(line: dict) -> str:
    payload = _payload(line)
    variable = str(payload.get("variableId") or "").strip()
    if variable:
        return f"var:{variable}"
    unit = str(line.get("unit") or payload.get("unit") or "").strip()
    if unit:
        return f"unit:{unit}"
    return "valor"


def _measure_label(line: dict, item: dict) -> str:
    name = str(_payload(line).get("variableName") or "").strip()
    if name:
        return name
    presentation = str(item.get("presentation") or "").split(". ")[0].strip()
    if presentation:
        return presentation
    return str(item.get("sourceId") or "Série publicada")


def _place_label(line: dict) -> str:
    payload = _payload(line)
    name = str(payload.get("territoryName") or payload.get("municipio") or "").strip()
    code = str(line.get("ibgeCode") or "").strip()
    if name and code:
        return f"{name} ({code})"
    if name:
        return name
    if code.isdigit() and len(code) >= 6:
        return f"Município {code}"
    if code:
        return code
    return "Sem código territorial"


def _slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts)[:48] or "medida"


def _groups(item: dict, lines: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for line in lines:
        if line.get("sourceId") != item.get("sourceId") or line.get("value") is None:
            continue
        grouped.setdefault(_measure_key(line), []).append(line)
    return grouped


def _unit_for(item: dict, rows: list[dict] | None = None) -> str:
    if rows:
        unit = str(rows[0].get("unit") or "").strip()
        if unit:
            return unit
    return "BRL" if item.get("financial") else "UNIT"


def _build_kpis(items: list[dict], lines: list[dict]) -> list[dict]:
    kpis: list[dict] = []
    for item in items:
        evidence = _evidence_ids(item)
        evidence_id = evidence[0] if evidence else None
        grouped = _groups(item, lines)
        if len(grouped) > 1:
            for key, rows in grouped.items():
                kpis.append(
                    {
                        "id": f"kpi-{_slug(item['sourceId'])}-{_slug(key)}",
                        "label": _measure_label(rows[0], item),
                        "value": sum(float(row["value"]) for row in rows),
                        "unit": _unit_for(item, rows),
                        "valueKind": item["valueKind"],
                        "sourceId": item["sourceId"],
                        "evidenceId": evidence_id,
                    }
                )
        elif item.get("numericTotal") is not None:
            rows = next(iter(grouped.values()), [])
            label = item.get("indicator") or item["sourceId"]
            if rows and _payload(rows[0]).get("variableName"):
                label = _measure_label(rows[0], item)
            kpis.append(
                {
                    "id": f"kpi-total-{item['sourceId']}",
                    "label": label,
                    "value": float(item["numericTotal"]),
                    "unit": _unit_for(item, rows or None),
                    "valueKind": item["valueKind"],
                    "sourceId": item["sourceId"],
                    "evidenceId": evidence_id,
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
                    "evidenceId": evidence_id,
                }
            )
    return kpis


def _build_charts(items: list[dict], lines: list[dict]) -> list[dict]:
    charts: list[dict] = []
    if not items:
        return charts
    coverage_points = [
        {"x": item["sourceId"], "y": float(item.get("coverageCount") or 0)} for item in items
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
            "series": [{"name": "Municípios ou registros na base", "points": coverage_points}],
            "evidenceIds": list(dict.fromkeys(evidence)),
        }
    )
    tops: list[dict] = []
    for item in items:
        grouped = _groups(item, lines)
        if len(grouped) > 1:
            for key, rows in grouped.items():
                charts.append(_total_chart(item, rows, key))
                tops.append(_top_chart(item, rows, key))
        else:
            rows = next(iter(grouped.values()), [])
            if item.get("numericTotal") is not None:
                charts.append(_total_chart(item, rows or None, "valor"))
            if rows:
                tops.append(_top_chart(item, rows, "valor"))
    if len(tops) == 1:
        tops[0]["id"] = "top-municipalities"
    charts.extend(tops)
    return charts


def _total_chart(item: dict, rows: list[dict] | None, key: str) -> dict:
    if rows:
        value = sum(float(row["value"]) for row in rows)
        label = _measure_label(rows[0], item)
        unit = _unit_for(item, rows)
    else:
        value = float(item["numericTotal"])
        label = _measure_label({}, item)
        unit = _unit_for(item)
    return {
        "id": f"total-{_slug(str(item['sourceId']))}-{_slug(key)}",
        "title": f"{label} por competência",
        "type": "bar",
        "unit": unit,
        "valueKind": item["valueKind"],
        "sourceId": item["sourceId"],
        "series": [
            {
                "name": label,
                "points": [{"x": str(item.get("competence") or item["sourceId"]), "y": value}],
            }
        ],
        "evidenceIds": _evidence_ids(item),
    }


def _top_chart(item: dict, rows: list[dict], key: str) -> dict:
    by_place: dict[str, float] = {}
    line_evidence: list[str] = []
    for row in rows:
        label = _place_label(row)
        by_place[label] = by_place.get(label, 0.0) + float(row["value"])
        line_id = row.get("id") or row.get("silverRowId")
        if line_id:
            line_evidence.append(str(line_id))
    ranked = sorted(by_place.items(), key=lambda pair: pair[1], reverse=True)[:TOP_N]
    label = _measure_label(rows[0], item)
    return {
        "id": f"top-{_slug(str(item['sourceId']))}-{_slug(key)}",
        "title": f"{label} — maiores municípios",
        "type": "bar",
        "unit": _unit_for(item, rows),
        "valueKind": item["valueKind"],
        "sourceId": item["sourceId"],
        "series": [
            {
                "name": label,
                "points": [{"x": place, "y": value} for place, value in ranked],
            }
        ],
        "evidenceIds": list(dict.fromkeys(line_evidence))[:50],
    }
