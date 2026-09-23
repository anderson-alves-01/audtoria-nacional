from sirta_api.domain.sidra_periods import catalog_for_sidra_period, sidra_comparison_periods


def test_catalog_for_sidra_period_points_the_endpoint_at_that_year() -> None:
    catalog = {
        "connector": "ibge_sidra_series",
        "endpoint": (
            "https://servicodados.ibge.gov.br/api/v3/agregados/5938/"
            "periodos/2023/variaveis/37|6575?localidades=N6[all]"
        ),
        "competence": "2023",
        "parameters": {
            "agregado": "5938",
            "periodo": "2023",
            "comparison_periodos": ["2021", "2022", "2023"],
        },
    }
    cloned = catalog_for_sidra_period(catalog, "2021")
    assert cloned["competence"] == "2021"
    assert cloned["parameters"]["periodo"] == "2021"
    assert "comparison_periodos" not in cloned["parameters"]
    assert "/periodos/2021/" in cloned["endpoint"]
    assert "/periodos/2023/" not in cloned["endpoint"]
    assert catalog["competence"] == "2023"


def test_sidra_comparison_periods_keep_only_four_digit_years_in_order() -> None:
    catalog = {
        "connector": "ibge_sidra_series",
        "parameters": {"comparison_periodos": ["2022", "2024", "ano", "2023"]},
    }
    assert sidra_comparison_periods(catalog) == ["2022", "2024", "2023"]
    assert sidra_comparison_periods({"connector": "siconfi_statement"}) == []
