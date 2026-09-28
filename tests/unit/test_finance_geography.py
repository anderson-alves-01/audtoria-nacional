from sirta_api.domain.finance_geography import aggregate_finance_geography


def test_map_keeps_one_realized_figure_per_state_and_ignores_forecast():
    view = aggregate_finance_geography(
        [
            {
                "sourceId": "TESOURO-FPM-VALORES",
                "ufCode": "12",
                "account": "",
                "column": "",
                "unit": "BRL",
                "competence": "2025",
                "total": 15,
                "municipalityCount": 2,
            },
            {
                "sourceId": "SICONFI-RREO",
                "ufCode": "12",
                "account": "ReceitasCorrentes",
                "column": "Previsão Atualizada",
                "unit": "BRL",
                "competence": "2025",
                "total": 999,
                "municipalityCount": 2,
            },
            {
                "sourceId": "SICONFI-RREO",
                "ufCode": "12",
                "account": "ReceitasCorrentes",
                "column": "Até o Bimestre",
                "unit": "BRL",
                "competence": "2025",
                "total": 40,
                "municipalityCount": 2,
            },
            {
                "sourceId": "SICONFI-DCA",
                "ufCode": "35",
                "account": "TotalReceitas",
                "column": "Receitas Brutas Realizadas",
                "unit": "BRL",
                "competence": "2024",
                "total": 999,
                "municipalityCount": 3,
            },
            {
                "sourceId": "SICONFI-DCA",
                "ufCode": "35",
                "account": "ReceitaOrcamentaria",
                "column": "Receitas Brutas Realizadas",
                "unit": "BRL",
                "competence": "2024",
                "total": 100,
                "municipalityCount": 3,
            },
            {
                "sourceId": "SICONFI-DCA",
                "ufCode": "35",
                "account": "ReceitaOrcamentaria",
                "column": "Receitas",
                "unit": "BRL",
                "competence": "2024",
                "total": 50,
                "municipalityCount": 3,
            },
            {
                "sourceId": "IBGE-SIDRA",
                "ufCode": "12",
                "account": "",
                "column": "",
                "unit": "Pessoas",
                "competence": "2024",
                "total": 8,
                "municipalityCount": 1,
            },
        ]
    )
    assert view["createsTaxCredit"] is False
    norte = next(region for region in view["regions"] if region["id"] == "norte")
    acre = next(state for state in norte["states"] if state["uf"] == "AC")
    assert acre["measures"] == [
        {
            "sourceId": "TESOURO-FPM-VALORES",
            "sourceLabel": "FPM publicado",
            "label": "FPM publicado",
            "unit": "BRL",
            "competence": "2025",
            "total": 15.0,
            "municipalityCount": 2,
        },
        {
            "sourceId": "SICONFI-RREO",
            "sourceLabel": "Receita corrente até o bimestre",
            "label": "Receita corrente até o bimestre",
            "unit": "BRL",
            "competence": "2025",
            "total": 40.0,
            "municipalityCount": 2,
        },
    ]
    sudeste = next(region for region in view["regions"] if region["id"] == "sudeste")
    sao_paulo = next(state for state in sudeste["states"] if state["uf"] == "SP")
    assert sao_paulo["measures"] == [
        {
            "sourceId": "SICONFI-DCA",
            "sourceLabel": "Receitas brutas realizadas",
            "label": "Receitas brutas realizadas",
            "unit": "BRL",
            "competence": "2024",
            "total": 100.0,
            "municipalityCount": 3,
        }
    ]


def test_empty_money_map_still_lists_every_region_without_a_number():
    view = aggregate_finance_geography([])
    assert [region["id"] for region in view["regions"]] == [
        "norte",
        "nordeste",
        "centro-oeste",
        "sudeste",
        "sul",
    ]
    assert all(
        state["measures"] == [] for region in view["regions"] for state in region["states"]
    )
