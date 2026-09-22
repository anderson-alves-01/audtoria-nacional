from sirta_api.domain.dashboard_charts import build_dashboard_visuals


def test_build_visuals_only_chartable_kinds() -> None:
    items = [
        {
            "goldId": "g1",
            "sourceId": "IBGE-SIDRA",
            "indicator": "population",
            "competence": "2024",
            "coverageCount": 5570,
            "numericTotal": 100.0,
            "valueKind": "REFERENCE_QUANTITY",
            "financial": False,
        },
        {
            "goldId": "g2",
            "sourceId": "TESOURO-TRANSPARENTE",
            "indicator": "dict",
            "competence": "2024",
            "coverageCount": 10,
            "numericTotal": None,
            "valueKind": "CATALOG_METADATA",
            "financial": False,
        },
        {
            "sourceId": "COVERAGE-DIVERGENCE",
            "coverageCount": 1,
            "valueKind": "COVERAGE_REGISTRY",
            "financial": False,
        },
    ]
    lines = [
        {
            "id": "l1",
            "sourceId": "IBGE-SIDRA",
            "ibgeCode": "3550308",
            "value": 50.0,
            "silverRowId": "r1",
        },
        {
            "id": "l2",
            "sourceId": "IBGE-SIDRA",
            "ibgeCode": "3304557",
            "value": 30.0,
            "silverRowId": "r2",
        },
    ]
    visuals = build_dashboard_visuals(items=items, lines=lines)
    assert len(visuals["kpis"]) == 2
    assert all(kpi["sourceId"] == "IBGE-SIDRA" for kpi in visuals["kpis"])
    assert visuals["kpis"][0]["evidenceId"] == "g1"
    chart_ids = {chart["id"] for chart in visuals["charts"]}
    assert "coverage-by-source" in chart_ids
    assert "top-municipalities" in chart_ids
    top = next(chart for chart in visuals["charts"] if chart["id"] == "top-municipalities")
    assert top["evidenceIds"]
    assert top["valueKind"] == "REFERENCE_QUANTITY"
    assert top["unit"] != "MIXED"
    assert top["series"][0]["points"][0]["x"] == "Município 3550308"
    totals = [chart for chart in visuals["charts"] if chart["id"].startswith("total-")]
    assert len(totals) == 1
    assert totals[0]["unit"] != "MIXED"
    assert totals[0]["valueKind"] == "REFERENCE_QUANTITY"


def test_distinct_measures_are_not_summed_or_called_transfers() -> None:
    items = [
        {
            "goldId": "g1",
            "sourceId": "IBGE-SIDRA-CEMP",
            "indicator": "ibge_cemp_municipal_totals",
            "competence": "2024",
            "coverageCount": 3,
            "numericTotal": 999.0,
            "valueKind": "REFERENCE_QUANTITY",
            "financial": False,
            "presentation": "Cadastro Central de Empresas. Não é base de ISS.",
        },
        {
            "goldId": "g2",
            "sourceId": "TESOURO-FPM-VALORES",
            "indicator": "tesouro_fpm_received",
            "competence": "2026-08",
            "coverageCount": 2,
            "numericTotal": 80.0,
            "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
            "financial": True,
        },
    ]
    lines = [
        {
            "id": "a",
            "sourceId": "IBGE-SIDRA-CEMP",
            "ibgeCode": "3550308",
            "value": 10.0,
            "unit": "Pessoas",
            "payload": {
                "variableId": "707",
                "variableName": "Pessoal ocupado",
                "territoryName": "São Paulo",
            },
        },
        {
            "id": "b",
            "sourceId": "IBGE-SIDRA-CEMP",
            "ibgeCode": "3550308",
            "value": 900.0,
            "unit": "Mil Reais",
            "payload": {
                "variableId": "662",
                "variableName": "Salários",
                "territoryName": "São Paulo",
            },
        },
        {
            "id": "c",
            "sourceId": "TESOURO-FPM-VALORES",
            "ibgeCode": "3550308",
            "value": 80.0,
            "unit": "BRL",
            "payload": {"territoryName": "São Paulo"},
        },
    ]
    visuals = build_dashboard_visuals(items=items, lines=lines)
    labels = [kpi["label"] for kpi in visuals["kpis"]]
    assert "Pessoal ocupado" in labels
    assert "Salários" in labels
    assert all(kpi["value"] != 999.0 for kpi in visuals["kpis"])
    cemp_charts = [
        chart
        for chart in visuals["charts"]
        if chart.get("sourceId") == "IBGE-SIDRA-CEMP" and chart["id"].startswith("top-")
    ]
    assert len(cemp_charts) == 2
    assert all(chart["valueKind"] == "REFERENCE_QUANTITY" for chart in cemp_charts)
    assert {chart["unit"] for chart in cemp_charts} == {"Pessoas", "Mil Reais"}
    assert all(
        chart["series"][0]["points"][0]["x"] == "São Paulo (3550308)" for chart in cemp_charts
    )
    fpm = next(
        chart
        for chart in visuals["charts"]
        if chart.get("sourceId") == "TESOURO-FPM-VALORES" and chart["id"].startswith("top-")
    )
    assert fpm["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert fpm["unit"] == "BRL"
    totals = [chart for chart in visuals["charts"] if chart["id"].startswith("total-")]
    assert totals
    assert all(chart["unit"] != "MIXED" and chart.get("sourceId") for chart in totals)


def test_empty_items_yield_empty_visuals() -> None:
    assert build_dashboard_visuals(items=[], lines=[]) == {"kpis": [], "charts": []}
