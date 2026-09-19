from pathlib import Path

from sirta_api.adapters.ingest.parsers import (
    parse_ibge_sidra_series,
    parse_state_ba_csv,
    parse_state_es_csv,
    parse_state_go_csv,
    parse_state_mg_csv,
    parse_state_pe_csv,
    parse_tesouro_monthly_csv,
)
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
    assert presentation_for("SICONFI-RGF")["isFiscalStatement"] is True
    assert presentation_for("SICONFI-RGF")["createsTaxCredit"] is False


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


def test_state_pe_csv_joins_ibge_and_publishes_zero_ipva() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/pe-transferencias-municipais-2024.csv"
    ).read_bytes()
    lookup = {
        ("ABREU E LIMA", "PE"): "2600054",
        ("RECIFE", "PE"): "2611606",
    }
    icms, quarantined_icms = parse_state_pe_csv(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"2600054", "2611606"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "PE" for row in icms)
    assert len(quarantined_icms) == 1
    ipva, quarantined_ipva = parse_state_pe_csv(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    abreu = next(row for row in ipva if row["ibgeCode"] == "2600054")
    assert abreu["value"] == 0.0
    assert abreu["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-IPVA-QUOTA")["createsTaxCredit"] is False


def test_state_ba_csv_parses_multi_header_and_joins_ibge() -> None:
    body = Path("tests/fixtures/official-snapshots/ba-repasses-municipios-2024.csv").read_bytes()
    lookup = {
        ("ABAIRA", "BA"): "2900108",
        ("ALAGOINHAS", "BA"): "2900702",
    }
    icms, quarantined_icms = parse_state_ba_csv(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"2900108", "2900702"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "BA" for row in icms)
    abaira = next(row for row in icms if row["ibgeCode"] == "2900108")
    assert abaira["value"] == 374980.42
    assert abaira["competence"] == "2024"
    assert len(quarantined_icms) == 1
    ipva, quarantined_ipva = parse_state_ba_csv(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    alagoinhas = next(row for row in ipva if row["ibgeCode"] == "2900702")
    assert alagoinhas["value"] == 1066957.0
    assert alagoinhas["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-BA-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-BA-IPVA-QUOTA")["createsTaxCredit"] is False


def test_state_mg_csv_joins_native_ibge_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/mg-ft-repasse-mun.csv").read_bytes()
    municipio = Path("tests/fixtures/official-snapshots/mg-dm-municipio.csv").read_bytes()
    tempo = Path("tests/fixtures/official-snapshots/mg-dm-tempo-mensal.csv").read_bytes()
    icms, quarantined_icms = parse_state_mg_csv(
        body, tax="ICMS", municipio_dim=municipio, tempo_dim=tempo
    )
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"3100104", "3106200"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "MG" for row in icms)
    assert all(row["competence"] == "2024-01" for row in icms)
    abadia = next(row for row in icms if row["ibgeCode"] == "3100104")
    assert abadia["value"] == 817661.12
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_mg_csv(
        body, tax="IPVA", municipio_dim=municipio, tempo_dim=tempo
    )
    assert len(ipva) == 2
    bh = next(row for row in ipva if row["ibgeCode"] == "3106200")
    assert bh["value"] == 817489013.21
    assert bh["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-MG-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-MG-IPVA-QUOTA")["createsTaxCredit"] is False


def test_state_es_csv_joins_native_ibge_and_quarantines_territory() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/es-transf-estado-municipios-2024.csv"
    ).read_bytes()
    icms, quarantined_icms = parse_state_es_csv(body, tax="ICMS")
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"3200102", "3205309"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "ES" for row in icms)
    assert all(row["competence"] == "2024-01" for row in icms)
    afonso = next(row for row in icms if row["ibgeCode"] == "3200102")
    assert afonso["value"] == 3268119.24
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_es_csv(body, tax="IPVA")
    assert len(ipva) == 2
    vitoria = next(row for row in ipva if row["ibgeCode"] == "3205309")
    assert vitoria["value"] == 4816186.84
    assert vitoria["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-ES-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-ES-IPVA-QUOTA")["createsTaxCredit"] is False


def test_state_go_csv_joins_name_uf_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/go-repasses-municipios-202608.csv").read_bytes()
    lookup = {
        ("ABADIA DE GOIAS", "GO"): "5200050",
        ("GOIANIA", "GO"): "5208707",
    }
    ipva, quarantined = parse_state_go_csv(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    assert {row["ibgeCode"] for row in ipva} == {"5200050", "5208707"}
    assert all(row["modality"] == "IPVA_QUOTA" for row in ipva)
    assert all(row["uf"] == "GO" for row in ipva)
    assert all(row["competence"] == "2026-08" for row in ipva)
    abadia = next(row for row in ipva if row["ibgeCode"] == "5200050")
    assert abadia["value"] == 13397.86
    goiania = next(row for row in ipva if row["ibgeCode"] == "5208707")
    assert goiania["value"] == 3513965.9
    assert len(quarantined) == 1
    assert quarantined[0][1] == "missing IBGE municipality code"
    assert presentation_for("ESTADO-GO-IPVA-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-GO-IPVA-QUOTA")["createsTaxCredit"] is False
