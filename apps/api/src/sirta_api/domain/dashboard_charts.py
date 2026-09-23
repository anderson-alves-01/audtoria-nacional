"""Build citável chart/KPI payloads from official Gold (reference / published transfers only)."""

from __future__ import annotations

import re

CHARTABLE_VALUE_KINDS = frozenset({"REFERENCE_QUANTITY", "TRANSFER_AMOUNT_AS_PUBLISHED"})
STATEMENT_COVERAGE_KINDS = frozenset({"FISCAL_STATEMENT_LINE"})
STATEMENT_REVENUE_SOURCES = ("SICONFI-RREO", "SICONFI-DCA")
STATEMENT_REVENUE_ACCOUNTS = {
    "SICONFI-RREO": frozenset({"ReceitaCorrente", "ReceitasCorrentes"}),
    "SICONFI-DCA": frozenset({"ReceitaOrcamentaria", "TotalReceitas"}),
}
STATEMENT_REVENUE_NOTE = (
    "Soma das linhas de receita já publicadas nesta carga. "
    "Não é o total nacional e não é valor a recuperar."
)
TOP_N = 10
_COMPETENCE = re.compile(r"\d{4}(?:-\d{2})?")


def statement_revenue_account_codes() -> frozenset[str]:
    codes: set[str] = set()
    for accounts in STATEMENT_REVENUE_ACCOUNTS.values():
        codes.update(accounts)
    return frozenset(codes)


def is_statement_revenue_cell(source_id: str, account: str, column: str) -> bool:
    """Parent published revenue only. Percent and balance columns stay out."""
    code = account.strip()
    label = column.strip()
    parents = STATEMENT_REVENUE_ACCOUNTS.get(source_id)
    if parents is None or code not in parents or not label:
        return False
    folded = label.casefold()
    if "%" in label or "saldo" in folded or "dedu" in folded:
        return False
    if source_id == "SICONFI-DCA":
        return folded in {"receitas", "receitas brutas realizadas"}
    if "previs" in folded and "atualizada" in folded:
        return True
    return "bimestre" in folded and not folded.startswith("no ")


def build_statement_revenue_charts(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = {}
    for row in rows:
        source_id = str(row.get("sourceId") or "")
        account = str(row.get("account") or "")
        column = str(row.get("column") or "")
        if not is_statement_revenue_cell(source_id, account, column):
            continue
        if row.get("value") is None:
            continue
        grouped.setdefault((source_id, account, column), []).append(row)
    charts: list[dict] = []
    for (source_id, account, column), cells in sorted(grouped.items()):
        points = [
            {"x": str(cell.get("competence") or ""), "y": float(cell["value"])}
            for cell in sorted(cells, key=lambda cell: str(cell.get("competence") or ""))
        ]
        evidence = [str(cell["evidenceId"]) for cell in cells if cell.get("evidenceId")]
        title = f"{_revenue_account_label(account)} — {_revenue_column_label(column)}"
        charts.append(
            {
                "id": f"revenue-{_slug(source_id)}-{_slug(account)}-{_slug(column)}",
                "title": title,
                "note": STATEMENT_REVENUE_NOTE,
                "type": "line" if len(points) > 1 else "bar",
                "unit": "BRL",
                "valueKind": "FISCAL_STATEMENT_LINE",
                "sourceId": source_id,
                "series": [{"name": title, "points": points}],
                "evidenceIds": list(dict.fromkeys(evidence)),
                "createsTaxCredit": False,
            }
        )
    return charts


def _revenue_account_label(account: str) -> str:
    labels = {
        "ReceitaCorrente": "Receita corrente",
        "ReceitasCorrentes": "Receita corrente",
        "ReceitaOrcamentaria": "Receita orçamentária",
        "TotalReceitas": "Total das receitas",
    }
    return labels.get(account, account)


def _revenue_column_label(column: str) -> str:
    folded = column.casefold()
    if "previs" in folded and "atualizada" in folded:
        return "previsão atualizada"
    if "bimestre" in folded:
        return "até o bimestre"
    if folded == "receitas brutas realizadas":
        return "receitas brutas realizadas"
    if folded == "receitas":
        return "receitas"
    return column


def items_for_chart_lines(items: list[dict]) -> list[dict]:
    """Statement rows stay on the coverage count. Their lines are not loaded."""
    return [
        item
        for item in items
        if item.get("valueKind") in CHARTABLE_VALUE_KINDS
        and item.get("sourceId") != "COVERAGE-DIVERGENCE"
    ]


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
    statements = [
        item
        for item in items
        if item.get("valueKind") in STATEMENT_COVERAGE_KINDS
        and item.get("sourceId") != "COVERAGE-DIVERGENCE"
    ]
    scoped = lines or []
    kpis = _build_kpis(chartable, scoped)
    charts = _build_charts(chartable, scoped, coverage_items=[*chartable, *statements])
    return {"kpis": kpis, "charts": charts}


def separate_measures(items: list[dict], lines: list[dict]) -> None:
    """Attach per-variable figures when a source mixes measures. Leaves numericTotal intact."""
    for item in items:
        grouped = _groups(item, lines, competence=_item_competence(item))
        if len(grouped) < 2:
            continue
        item["measures"] = [
            {
                "label": _measure_label(rows[0], item),
                "unit": str(rows[0].get("unit") or "UNIT"),
                "value": sum(float(row["value"]) for row in rows),
                "count": sum(int(_payload(row).get("rowCount") or 1) for row in rows),
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


def _item_competence(item: dict) -> str | None:
    raw = str(item.get("competence") or "")[:7]
    return raw or None


def _row_year(line: dict) -> str:
    match = _COMPETENCE.fullmatch(str(_payload(line).get("competence") or ""))
    return match.group(0)[:7] if match else ""


def _dedupe_variable_cells(rows: list[dict]) -> list[dict]:
    """Keep one published cell when two runs repeat the same municipality, variable and year."""
    seen: set[tuple[str, str, str]] = set()
    kept: list[dict] = []
    for row in rows:
        variable = str(_payload(row).get("variableId") or "").strip()
        year = _row_year(row)
        if variable and year:
            key = (str(row.get("ibgeCode") or ""), variable, year)
            if key in seen:
                continue
            seen.add(key)
        kept.append(row)
    return kept


def _latest_item(items: list[dict]) -> dict:
    return max(items, key=lambda item: str(item.get("competence") or ""))


def _rows_for_ranking(rows: list[dict]) -> list[dict]:
    rows = _dedupe_variable_cells(rows)
    years = {year for row in rows if (year := _row_year(row))}
    if len(years) <= 1:
        return rows
    latest = max(years)
    return [row for row in rows if _row_year(row) == latest]


def _groups(
    item: dict,
    lines: list[dict],
    *,
    competence: str | None = None,
) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for line in lines:
        if line.get("sourceId") != item.get("sourceId") or line.get("value") is None:
            continue
        year = _row_year(line)
        if competence and year and year != competence:
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
    by_source: dict[str, list[dict]] = {}
    for item in items:
        by_source.setdefault(str(item["sourceId"]), []).append(item)
    kpis: list[dict] = []
    for siblings in by_source.values():
        years = {str(item.get("competence") or "") for item in siblings}
        chosen = [_latest_item(siblings)] if len(years) > 1 else siblings
        for item in chosen:
            kpis.extend(_kpis_for_item(item, lines))
    return kpis


def _kpis_for_item(item: dict, lines: list[dict]) -> list[dict]:
    kpis: list[dict] = []
    evidence = _evidence_ids(item)
    evidence_id = evidence[0] if evidence else None
    grouped = _groups(item, lines, competence=_item_competence(item))
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


def _build_charts(
    items: list[dict],
    lines: list[dict],
    coverage_items: list[dict] | None = None,
) -> list[dict]:
    charts: list[dict] = []
    covered = items if coverage_items is None else coverage_items
    if covered:
        coverage_points = _coverage_points(covered)
        evidence: list[str] = []
        for item in covered:
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
    if not items:
        return charts
    tops: list[dict] = []
    by_source: dict[str, list[dict]] = {}
    for item in items:
        by_source.setdefault(str(item["sourceId"]), []).append(item)
    for siblings in by_source.values():
        item = _latest_item(siblings)
        grouped = _groups(item, lines)
        if len(grouped) > 1:
            for key, rows in grouped.items():
                charts.append(_total_chart(item, rows, key, siblings))
                ranked = _rows_for_ranking(rows)
                if ranked:
                    tops.append(_top_chart(item, ranked, key))
        else:
            rows = next(iter(grouped.values()), [])
            if item.get("numericTotal") is not None:
                charts.append(_total_chart(item, rows or None, "valor", siblings))
            if rows:
                ranked = _rows_for_ranking(rows)
                if ranked:
                    tops.append(_top_chart(item, ranked, "valor"))
    if len(tops) == 1:
        tops[0]["id"] = "top-municipalities"
    charts.extend(tops)
    return charts


def _coverage_points(items: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(str(item["sourceId"]), []).append(item)
    points: list[dict] = []
    for source, siblings in grouped.items():
        years = {str(item.get("competence") or "") for item in siblings}
        if len(years) > 1:
            chosen = _latest_item(siblings)
            value = float(chosen.get("coverageCount") or 0)
        else:
            value = sum(float(item.get("coverageCount") or 0) for item in siblings)
        points.append({"x": source, "y": value})
    return points


def _total_chart(
    item: dict,
    rows: list[dict] | None,
    key: str,
    siblings: list[dict],
) -> dict:
    evidence: list[str] = []
    for sibling in siblings:
        evidence.extend(_evidence_ids(sibling))
    if rows:
        buckets: dict[str, float] = {}
        for row in _dedupe_variable_cells(rows):
            year = _row_year(row) or str(item.get("competence") or item["sourceId"])[:7]
            buckets[year] = buckets.get(year, 0.0) + float(row["value"])
        label = _measure_label(rows[0], item)
        unit = _unit_for(item, rows)
    else:
        year = str(item.get("competence") or item["sourceId"])
        buckets = {year: float(item["numericTotal"])}
        label = _measure_label({}, item)
        unit = _unit_for(item)
    points = [{"x": year, "y": value} for year, value in sorted(buckets.items())]
    return {
        "id": f"total-{_slug(str(item['sourceId']))}-{_slug(key)}",
        "title": f"{label} por competência",
        "type": "line" if len(points) > 1 else "bar",
        "unit": unit,
        "valueKind": item["valueKind"],
        "sourceId": item["sourceId"],
        "series": [{"name": label, "points": points}],
        "evidenceIds": list(dict.fromkeys(evidence)),
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
