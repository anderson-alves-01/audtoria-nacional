from sirta_api.domain.executive_geography import (
    aggregate_executive_geography,
    region_for_ibge,
)


def test_acre_municipality_falls_in_norte_and_the_sum_matches_published_lines():
    located = region_for_ibge("1200013")
    assert located is not None
    assert located[0] == "norte"
    view = aggregate_executive_geography(
        [
            {
                "sourceId": "IBGE-SIDRA",
                "ibgeCode": "1200013",
                "variableName": "População residente estimada",
                "unit": "Pessoas",
                "competence": "2024",
                "value": 10,
            },
            {
                "sourceId": "IBGE-SIDRA",
                "ibgeCode": "1200054",
                "variableName": "População residente estimada",
                "unit": "Pessoas",
                "competence": "2024",
                "value": 5,
            },
            {
                "sourceId": "SICONFI-RREO",
                "ibgeCode": "1200013",
                "variableName": "Receita",
                "unit": "BRL",
                "competence": "2025",
                "value": 999,
            },
        ]
    )
    assert view["createsTaxCredit"] is False
    norte = next(region for region in view["regions"] if region["id"] == "norte")
    acre = next(state for state in norte["states"] if state["uf"] == "AC")
    assert acre["measures"] == [
        {
            "sourceId": "IBGE-SIDRA",
            "sourceLabel": "IBGE — população",
            "label": "População residente estimada",
            "unit": "Pessoas",
            "competence": "2024",
            "total": 15.0,
            "municipalityCount": 2,
        }
    ]
    assert all(state["measures"] == [] for state in norte["states"] if state["uf"] != "AC")


def test_source_without_lines_does_not_produce_a_number():
    view = aggregate_executive_geography([])
    assert view["createsTaxCredit"] is False
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
