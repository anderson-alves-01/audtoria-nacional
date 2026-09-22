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
    assert "total-by-competence" in chart_ids
    assert "top-municipalities" in chart_ids
    top = next(chart for chart in visuals["charts"] if chart["id"] == "top-municipalities")
    assert top["evidenceIds"]
    assert top["series"][0]["points"][0]["x"] == "3550308"


def test_empty_items_yield_empty_visuals() -> None:
    assert build_dashboard_visuals(items=[], lines=[]) == {"kpis": [], "charts": []}
