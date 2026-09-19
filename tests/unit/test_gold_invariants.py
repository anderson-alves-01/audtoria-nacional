from pathlib import Path

from sirta_api.adapters.ingest.parsers import parse_ibge_sidra_series, parse_tesouro_monthly_csv
from sirta_api.domain.catalog import creates_tax_credit
from sirta_api.domain.gold import (
    assert_gold_lineage_complete,
    coverage_divergence,
    presentation_for,
)


def test_gold_lineage_rejects_incomplete_line() -> None:
    try:
        assert_gold_lineage_complete({"silverRowId": "1"})
    except ValueError as exc:
        assert "lineage" in str(exc)
        return
    raise AssertionError("expected lineage ValueError")


def test_quarantined_records_cannot_become_gold() -> None:
    try:
        assert_gold_lineage_complete(
            {
                "silverRowId": "1",
                "bronzeSha256": "a" * 64,
                "checksumSha256": "a" * 64,
                "landingManifestPath": "var/datalake/landing/manifest.json",
                "officialUrl": "https://sidra.ibge.gov.br/tabela/6579",
                "layer": "quarantine",
            }
        )
    except ValueError as exc:
        assert "Quarantined" in str(exc)
        return
    raise AssertionError("expected quarantine ValueError")


def test_catalog_metadata_is_not_financial() -> None:
    presentation = presentation_for("TESOURO-TRANSPARENTE")
    assert presentation["valueKind"] == "CATALOG_METADATA"
    assert presentation["financial"] is False
    assert presentation["createsTaxCredit"] is False
    assert presentation_for("SICONFI-ENTES")["isCoverageRegistry"] is True
    assert presentation_for("SICONFI-ENTES")["isFiscalStatement"] is False
    assert presentation_for("SICONFI-RREO")["isFiscalStatement"] is True


def test_public_source_cannot_create_credit_or_collection() -> None:
    assert creates_tax_credit("OFFICIAL_TRANSFER") is False
    assert creates_tax_credit("REFERENCE_ENRICHMENT") is False
    assert presentation_for("TESOURO-FPM-VALORES")["createsCollection"] is False
    assert presentation_for("IBGE-SIDRA")["createsTaxCredit"] is False


def test_sidra_6575_stays_quarantined_without_interpolation() -> None:
    body = Path("tests/fixtures/official-snapshots/ibge-5938.json").read_bytes()
    silver, quarantined = parse_ibge_sidra_series(body)
    assert all(row["variableId"] != "6575" for row in silver)
    assert any("..." in str(row[0].get("value")) for row in quarantined)
    quarantined_6575 = [row for row in quarantined if row[0].get("variableId") == "6575"]
    assert all(reason == "missing value" for _row, reason in quarantined_6575)


def test_coverage_divergence_explains_5571_versus_5570() -> None:
    item = coverage_divergence(
        [
            {"sourceId": "IBGE-SIDRA", "coverageCount": 5571},
            {"sourceId": "SICONFI-ENTES", "coverageCount": 5570},
            {"sourceId": "IBGE-SIDRA-PIB", "coverageCount": 5570},
        ]
    )
    assert item is not None
    assert item["status"] == "COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION"
    assert "5.571 versus 5.570" in item["explanation"]
    assert item["createsTaxCredit"] is False
    assert item["financial"] is False


def test_tesouro_monthly_csv_joins_ibge_and_keeps_fundeb_retention() -> None:
    body = Path("tests/fixtures/official-snapshots/tesouro-fpm-202608.csv").read_bytes()
    lookup = {
        ("COLINAS", "MA"): "2103505",
        ("CONCEICAO DO LAGO-ACU", "MA"): "2103554",
    }
    silver, quarantined = parse_tesouro_monthly_csv(body, ibge_lookup=lookup)
    assert len(quarantined) == 1
    modalities = {row["modality"] for row in silver}
    assert "FPM_RECEIVED" in modalities
    assert "FPM_TO_FUNDEB" in modalities
    received = [row for row in silver if row["modality"] == "FPM_RECEIVED"]
    assert {row["ibgeCode"] for row in received} == {"2103505", "2103554"}
    assert sum(row["value"] for row in received) == 356.0
