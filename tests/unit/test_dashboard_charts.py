from sirta_api.domain.dashboard_charts import (
    build_dashboard_visuals,
    build_statement_revenue_charts,
    items_for_chart_lines,
)


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


def test_same_measure_across_years_is_one_line_and_ranking_uses_the_latest_year() -> None:
    items = [
        {
            "goldId": "g2022",
            "sourceId": "IBGE-SIDRA-PIB",
            "indicator": "ibge_gdp_and_services_va",
            "competence": "2022",
            "coverageCount": 2,
            "numericTotal": 30.0,
            "valueKind": "REFERENCE_QUANTITY",
            "financial": False,
        },
        {
            "goldId": "g2023",
            "sourceId": "IBGE-SIDRA-PIB",
            "indicator": "ibge_gdp_and_services_va",
            "competence": "2023",
            "coverageCount": 2,
            "numericTotal": 80.0,
            "valueKind": "REFERENCE_QUANTITY",
            "financial": False,
        },
    ]
    lines = [
        {
            "id": "a",
            "sourceId": "IBGE-SIDRA-PIB",
            "ibgeCode": "3550308",
            "value": 10.0,
            "unit": "Mil Reais",
            "payload": {
                "variableId": "37",
                "variableName": "PIB",
                "territoryName": "São Paulo",
                "competence": "2022",
            },
        },
        {
            "id": "b",
            "sourceId": "IBGE-SIDRA-PIB",
            "ibgeCode": "3304557",
            "value": 20.0,
            "unit": "Mil Reais",
            "payload": {
                "variableId": "37",
                "variableName": "PIB",
                "territoryName": "Rio de Janeiro",
                "competence": "2022",
            },
        },
        {
            "id": "c",
            "sourceId": "IBGE-SIDRA-PIB",
            "ibgeCode": "3550308",
            "value": 50.0,
            "unit": "Mil Reais",
            "payload": {
                "variableId": "37",
                "variableName": "PIB",
                "territoryName": "São Paulo",
                "competence": "2023",
            },
        },
        {
            "id": "d",
            "sourceId": "IBGE-SIDRA-PIB",
            "ibgeCode": "3304557",
            "value": 30.0,
            "unit": "Mil Reais",
            "payload": {
                "variableId": "37",
                "variableName": "PIB",
                "territoryName": "Rio de Janeiro",
                "competence": "2023",
            },
        },
        {
            "id": "dup",
            "sourceId": "IBGE-SIDRA-PIB",
            "ibgeCode": "3550308",
            "value": 50.0,
            "unit": "Mil Reais",
            "payload": {
                "variableId": "37",
                "variableName": "PIB",
                "territoryName": "São Paulo",
                "competence": "2023",
            },
        },
    ]
    visuals = build_dashboard_visuals(items=items, lines=lines)
    totals = [chart for chart in visuals["charts"] if chart["id"].startswith("total-")]
    assert len(totals) == 1
    assert totals[0]["type"] == "line"
    assert totals[0]["series"][0]["points"] == [
        {"x": "2022", "y": 30.0},
        {"x": "2023", "y": 80.0},
    ]
    assert totals[0]["evidenceIds"] == ["g2022", "g2023"]
    top = next(chart for chart in visuals["charts"] if chart["id"] == "top-municipalities")
    assert top["series"][0]["points"][0] == {"x": "São Paulo (3550308)", "y": 50.0}
    assert all(point["y"] != 60.0 for point in top["series"][0]["points"])
    total_kpis = [kpi for kpi in visuals["kpis"] if kpi["id"].startswith("kpi-total")]
    assert len(total_kpis) == 1
    assert total_kpis[0]["value"] == 80.0


def test_statement_lines_join_coverage_and_stay_out_of_money_charts() -> None:
    items = [
        {
            "goldId": "fpm",
            "sourceId": "TESOURO-FPM-VALORES",
            "indicator": "fpm",
            "competence": "2026-08",
            "coverageCount": 5570,
            "numericTotal": 80.0,
            "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
            "financial": True,
        },
        {
            "goldId": "rreo-1",
            "sourceId": "SICONFI-RREO",
            "indicator": "siconfi_rreo",
            "competence": "2025",
            "coverageCount": 100,
            "numericTotal": 999_999.0,
            "valueKind": "FISCAL_STATEMENT_LINE",
            "financial": True,
        },
        {
            "goldId": "rreo-2",
            "sourceId": "SICONFI-RREO",
            "indicator": "siconfi_rreo",
            "competence": "2025",
            "coverageCount": 40,
            "numericTotal": 1.0,
            "valueKind": "FISCAL_STATEMENT_LINE",
            "financial": True,
        },
    ]
    lines = [
        {
            "id": "line-rreo",
            "sourceId": "SICONFI-RREO",
            "ibgeCode": "3550308",
            "value": 999_999.0,
            "unit": "BRL",
            "silverRowId": "row-rreo",
        }
    ]
    visuals = build_dashboard_visuals(items=items, lines=lines)
    coverage = next(chart for chart in visuals["charts"] if chart["id"] == "coverage-by-source")
    points = {point["x"]: point["y"] for point in coverage["series"][0]["points"]}
    assert points["SICONFI-RREO"] == 140
    assert points["TESOURO-FPM-VALORES"] == 5570
    assert coverage["unit"] == "COUNT"
    money = [chart for chart in visuals["charts"] if chart["id"] != "coverage-by-source"]
    assert all("siconfi-rreo" not in chart["id"] for chart in money)
    assert all(chart.get("sourceId") != "SICONFI-RREO" for chart in money)
    brl_sources = {chart.get("sourceId") for chart in money if chart["unit"] == "BRL"}
    assert brl_sources <= {"TESOURO-FPM-VALORES"}
    assert all(kpi["sourceId"] != "SICONFI-RREO" for kpi in visuals["kpis"])
    loaded = items_for_chart_lines(items)
    assert [item["sourceId"] for item in loaded] == ["TESOURO-FPM-VALORES"]


def test_parent_revenue_columns_stay_separate_and_do_not_become_a_gap() -> None:
    charts = build_statement_revenue_charts(
        [
            {
                "sourceId": "SICONFI-RREO",
                "account": "ReceitasCorrentes",
                "column": "PREVISÃO ATUALIZADA (a)",
                "competence": "2025",
                "value": 100.0,
                "evidenceId": "g-prev",
            },
            {
                "sourceId": "SICONFI-RREO",
                "account": "ReceitasCorrentes",
                "column": "Até o Bimestre (c)",
                "competence": "2025",
                "value": 80.0,
                "evidenceId": "g-real",
            },
            {
                "sourceId": "SICONFI-RREO",
                "account": "ReceitaCorrente",
                "column": "Até o Bimestre",
                "competence": "2025",
                "value": 123.45,
                "evidenceId": "g-fixture",
            },
            {
                "sourceId": "SICONFI-RREO",
                "account": "ReceitasCorrentes",
                "column": "% (c/a)",
                "competence": "2025",
                "value": 99.0,
            },
            {
                "sourceId": "SICONFI-RREO",
                "account": "ReceitasCorrentes",
                "column": "SALDO (a-c)",
                "competence": "2025",
                "value": 20.0,
            },
            {
                "sourceId": "SICONFI-RREO",
                "account": "DespesaPessoal",
                "column": "Até o Bimestre (c)",
                "competence": "2025",
                "value": 45.0,
            },
            {
                "sourceId": "SICONFI-RREO",
                "account": "ReceitaTributaria",
                "column": "Até o Bimestre (c)",
                "competence": "2025",
                "value": 10.0,
            },
            {
                "sourceId": "SICONFI-DCA",
                "account": "TotalReceitas",
                "column": "Receitas Brutas Realizadas",
                "competence": "2024",
                "value": 88.0,
                "evidenceId": "g-dca",
            },
            {
                "sourceId": "SICONFI-DCA",
                "account": "ReceitaOrcamentaria",
                "column": "Receitas",
                "competence": "2024",
                "value": 70.0,
            },
            {
                "sourceId": "SICONFI-DCA",
                "account": "TotalReceitas",
                "column": "Deduções - FUNDEB",
                "competence": "2024",
                "value": 5.0,
            },
        ]
    )
    values = sorted(point["y"] for chart in charts for point in chart["series"][0]["points"])
    assert values == [70.0, 80.0, 88.0, 100.0, 123.45]
    assert all(chart["createsTaxCredit"] is False for chart in charts)
    assert all(chart["unit"] == "BRL" for chart in charts)
    assert all("valor a recuperar" in chart["note"] for chart in charts)
    assert all("total nacional" in chart["note"] for chart in charts)
    realized = next(chart for chart in charts if chart["evidenceIds"] == ["g-real"])
    forecast = next(chart for chart in charts if chart["evidenceIds"] == ["g-prev"])
    assert realized["series"][0]["points"] == [{"x": "2025", "y": 80.0}]
    assert forecast["series"][0]["points"] == [{"x": "2025", "y": 100.0}]
    assert "Receita corrente" in realized["title"]
    assert "até o bimestre" in realized["title"]
