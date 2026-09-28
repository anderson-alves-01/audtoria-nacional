from sirta_api.domain.dashboards import fold_statement_gold_items


def test_fold_statement_slices_sums_one_competence_and_keeps_transfers() -> None:
    items = [
        {
            "sourceId": "SICONFI-DCA",
            "valueKind": "FISCAL_STATEMENT_LINE",
            "competence": "2024",
            "coverageCount": 10,
            "quarantinedCount": 1,
            "lineageLineCount": 10,
            "goldId": "a",
        },
        {
            "sourceId": "SICONFI-DCA",
            "valueKind": "FISCAL_STATEMENT_LINE",
            "competence": "2024",
            "coverageCount": 12,
            "quarantinedCount": 0,
            "lineageLineCount": 12,
            "goldId": "b",
        },
        {
            "sourceId": "TESOURO-FPM-VALORES",
            "valueKind": "TRANSFER_AMOUNT_AS_PUBLISHED",
            "competence": "2025-01",
            "coverageCount": 5547,
            "goldId": "c",
        },
    ]

    folded = fold_statement_gold_items(items)

    assert len(folded) == 2
    dca = next(item for item in folded if item["sourceId"] == "SICONFI-DCA")
    assert dca["coverageCount"] == 22
    assert dca["lineageLineCount"] == 22
    assert dca["quarantinedCount"] == 1
    assert dca["goldId"] == "a"
    fpm = next(item for item in folded if item["sourceId"] == "TESOURO-FPM-VALORES")
    assert fpm["coverageCount"] == 5547
