from pathlib import Path

from sirta_api.adapters.ingest.parsers import (
    parse_anatel_dados_gov,
    parse_aneel_ckan_open,
    parse_anp_revendedores_api,
    parse_bcb_sgs_olinda,
    parse_cnes_datasus_open,
    parse_epe_open_files,
    parse_ibge_sidra_series,
    parse_state_ac_csv,
    parse_state_ac_transparencia_json,
    parse_state_al_xls,
    parse_state_ba_csv,
    parse_state_ce_xls,
    parse_state_es_csv,
    parse_state_go_csv,
    parse_state_go_economia_xlsx,
    parse_state_ma_xls,
    parse_state_mg_csv,
    parse_state_ms_csv,
    parse_state_pa_icms_verde_xlsx,
    parse_state_pe_csv,
    parse_state_pi_repasseweb_html,
    parse_state_pr_html,
    parse_state_rn_xls,
    parse_state_ro_csv,
    parse_state_rs_xls,
    parse_tesouro_coint_municipio_csv,
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


def test_sidra_9509_cemp_publishes_reference_quantities_without_credit() -> None:
    body = Path("tests/fixtures/official-snapshots/ibge-9509.json").read_bytes()
    silver, quarantined = parse_ibge_sidra_series(body)
    assert quarantined == []
    assert len(silver) == 6
    assert {row["variableId"] for row in silver} == {"707", "662", "367"}
    assert {row["competence"] for row in silver} == {"2024"}
    assert all(row["territorialLevel"] == "N6" for row in silver)
    presentation = presentation_for("IBGE-SIDRA-CEMP")
    assert presentation["valueKind"] == "REFERENCE_QUANTITY"
    assert presentation["createsTaxCredit"] is False
    assert "crédito" in presentation["label"].lower() or "ISS" in presentation["label"]


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
    silver, quarantined = parse_tesouro_monthly_csv(
        body, ibge_lookup=lookup, item_allowlist=["FPM"], transfer_name="FPM"
    )
    assert len(quarantined) == 1
    modalities = {row["modality"] for row in silver}
    assert "FPM_RECEIVED" in modalities
    assert "FPM_TO_FUNDEB" in modalities
    received = [row for row in silver if row["modality"] == "FPM_RECEIVED"]
    assert {row["ibgeCode"] for row in received} == {"2103505", "2103554"}
    assert sum(row["value"] for row in received) == 356.0


def test_tesouro_monthly_csv_itr_ipi_exp_royalties_allowlists() -> None:
    body = Path("tests/fixtures/official-snapshots/tesouro-fpm-202608.csv").read_bytes()
    lookup = {
        ("COLINAS", "MA"): "2103505",
        ("CONCEICAO DO LAGO-ACU", "MA"): "2103554",
    }
    itr, itr_q = parse_tesouro_monthly_csv(
        body, ibge_lookup=lookup, item_allowlist=["ITR"], transfer_name="ITR"
    )
    assert len(itr_q) == 1
    assert {row["modality"] for row in itr} == {"ITR_RECEIVED", "ITR_TO_FUNDEB"}
    assert sum(row["value"] for row in itr if row["modality"] == "ITR_RECEIVED") == 39.0
    ipi, ipi_q = parse_tesouro_monthly_csv(
        body, ibge_lookup=lookup, item_allowlist=["IPI-EXP"], transfer_name="IPI-EXP"
    )
    assert ipi_q == []
    assert all(row["modality"] == "IPI_EXP_TO_FUNDEB" for row in ipi)
    assert sum(row["value"] for row in ipi) == 81.0
    roy, roy_q = parse_tesouro_monthly_csv(
        body,
        ibge_lookup=lookup,
        destination_allowlist=["Royalties"],
        transfer_name="Royalties",
    )
    assert roy_q == []
    assert all(row["modality"] == "ROYALTY_RECEIVED" for row in roy)
    assert {row["itemName"] for row in roy} == {"FEP", "CFEM", "ANP"}
    assert sum(row["value"] for row in roy) == 170.0
    assert presentation_for("TESOURO-ITR-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-IPI-EXP-VALORES")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )
    assert presentation_for("TESOURO-ROYALTIES-VALORES")["createsCollection"] is False


def test_tesouro_monthly_csv_lc176_allowlist() -> None:
    body = Path("tests/fixtures/official-snapshots/tesouro-fpm-202608.csv").read_bytes()
    lookup = {
        ("COLINAS", "MA"): "2103505",
        ("CONCEICAO DO LAGO-ACU", "MA"): "2103554",
    }
    silver, quarantined = parse_tesouro_monthly_csv(
        body,
        ibge_lookup=lookup,
        item_allowlist=["LC 176/2020 (ADO25)"],
        transfer_name="LC176",
    )
    assert len(quarantined) == 1
    assert all(row["modality"] == "LC176_RECEIVED" for row in silver)
    assert all(row["transferName"] == "LC176" for row in silver)
    assert {row["ibgeCode"] for row in silver} == {"2103505", "2103554"}
    assert sum(row["value"] for row in silver) == 126.0
    assert presentation_for("TESOURO-LC176-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-LC176-VALORES")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )


def test_tesouro_monthly_csv_iof_ouro_allowlist() -> None:
    body = Path("tests/fixtures/official-snapshots/tesouro-fpm-202608.csv").read_bytes()
    lookup = {
        ("COLINAS", "MA"): "2103505",
        ("CONCEICAO DO LAGO-ACU", "MA"): "2103554",
    }
    silver, quarantined = parse_tesouro_monthly_csv(
        body,
        ibge_lookup=lookup,
        item_allowlist=["IOF Ouro"],
        transfer_name="IOF-Ouro",
    )
    assert len(quarantined) == 1
    assert all(row["modality"] == "IOF_OURO_RECEIVED" for row in silver)
    assert all(row["transferName"] == "IOF-Ouro" for row in silver)
    assert {row["ibgeCode"] for row in silver} == {"2103505", "2103554"}
    assert sum(row["value"] for row in silver) == 21.0
    assert presentation_for("TESOURO-IOF-OURO-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-IOF-OURO-VALORES")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )


def test_tesouro_monthly_csv_fundeb_complement_allowlist() -> None:
    body = Path("tests/fixtures/official-snapshots/tesouro-fpm-202608.csv").read_bytes()
    lookup = {
        ("COLINAS", "MA"): "2103505",
        ("CONCEICAO DO LAGO-ACU", "MA"): "2103554",
    }
    silver, quarantined = parse_tesouro_monthly_csv(
        body,
        ibge_lookup=lookup,
        item_allowlist=[
            "COUN VAAT",
            "COUN VAAR",
            "COUN VAAF",
            "AJUSTE FUNDEB VAAT",
        ],
        transfer_name="FDB-COMP",
    )
    assert len(quarantined) == 1
    assert len(silver) == 5
    assert all(row["transferName"] == "FDB-COMP" for row in silver)
    assert {row["modality"] for row in silver} == {
        "FDB_COMP_TO_FUNDEB",
        "FDB_COMP_TO_AJUSTE_FUNDEB",
    }
    assert {row["ibgeCode"] for row in silver} == {"2103505", "2103554"}
    assert sum(row["value"] for row in silver) == 108.0
    assert all(len(row["rowId"]) <= 64 for row in silver)
    assert len({row["rowId"] for row in silver}) == 5
    assert presentation_for("TESOURO-FUNDEB-COMPLEMENT-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-FUNDEB-COMPLEMENT-VALORES")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )


def test_tesouro_coint_lc87_wide_csv() -> None:
    lookup = {
        ("ACRELANDIA", "AC"): "1200013",
        ("ASSIS BRASIL", "AC"): "1200054",
    }
    body = Path("tests/fixtures/official-snapshots/tesouro-lc8796-por-municipio.csv").read_bytes()
    silver, quarantined = parse_tesouro_coint_municipio_csv(
        body,
        ibge_lookup=lookup,
        transfer_name="LC 87/96",
        competence="2018-01",
    )
    assert len(quarantined) == 1
    assert all(row["modality"] == "LC87_RECEIVED" for row in silver)
    assert all(row["transferName"] == "LC 87/96" for row in silver)
    assert all(row["competence"] == "2018-01" for row in silver)
    assert {row["ibgeCode"] for row in silver} == {"1200013", "1200054"}
    assert sum(row["value"] for row in silver) == 376.76 + 428.92
    assert presentation_for("TESOURO-LC87-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-LC87-VALORES")["valueKind"] == ("TRANSFER_AMOUNT_AS_PUBLISHED")


def test_tesouro_coint_remaining_wide_csv() -> None:
    lookup = {
        ("ACRELANDIA", "AC"): "1200013",
        ("ASSIS BRASIL", "AC"): "1200054",
    }
    fpm_body = Path(
        "tests/fixtures/official-snapshots/tesouro-fpm-por-municipio.csv"
    ).read_bytes()
    fpm, fpm_q = parse_tesouro_coint_municipio_csv(
        fpm_body,
        ibge_lookup=lookup,
        transfer_name="FPM",
        competence="2025-01",
    )
    assert len(fpm_q) == 1
    assert all(row["modality"] == "FPM_RECEIVED" for row in fpm)
    assert {row["ibgeCode"] for row in fpm} == {"1200013", "1200054"}
    assert sum(row["value"] for row in fpm) == 1408936.79 + 1112480.55
    assert presentation_for("TESOURO-FPM-COINT-VALORES")["createsTaxCredit"] is False
    itr_body = Path(
        "tests/fixtures/official-snapshots/tesouro-itr-por-municipio.csv"
    ).read_bytes()
    itr, itr_q = parse_tesouro_coint_municipio_csv(
        itr_body,
        ibge_lookup=lookup,
        transfer_name="ITR",
        competence="2025-01",
    )
    assert len(itr_q) == 1
    assert all(row["modality"] == "ITR_RECEIVED" for row in itr)
    assert sum(row["value"] for row in itr) == 77.05 + 61.20
    assert presentation_for("TESOURO-ITR-COINT-VALORES")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )
    iof_body = Path(
        "tests/fixtures/official-snapshots/tesouro-iof-por-municipio.csv"
    ).read_bytes()
    iof, iof_q = parse_tesouro_coint_municipio_csv(
        iof_body,
        ibge_lookup=lookup,
        transfer_name="IOF-Ouro",
        competence="2014-07",
    )
    assert len(iof_q) == 1
    assert all(row["modality"] == "IOF_OURO_RECEIVED" for row in iof)
    assert {row["ibgeCode"] for row in iof} == {"1200013", "1200054"}
    assert sum(row["value"] for row in iof) == 72.98 + 55.40
    assert presentation_for("TESOURO-IOF-OURO-COINT-VALORES")["createsTaxCredit"] is False
    lc176_body = Path(
        "tests/fixtures/official-snapshots/tesouro-lc176-por-municipio.csv"
    ).read_bytes()
    lc176, lc176_q = parse_tesouro_coint_municipio_csv(
        lc176_body,
        ibge_lookup=lookup,
        transfer_name="LC 176/2020",
        competence="2025-01",
    )
    assert len(lc176_q) == 1
    assert all(row["modality"] == "LC176_RECEIVED" for row in lc176)
    assert all(row["transferName"] == "LC 176/2020" for row in lc176)
    assert sum(row["value"] for row in lc176) == 962.01 + 720.00
    assert presentation_for("TESOURO-LC176-COINT-VALORES")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )


def test_tesouro_coint_fundeb_wide_csv() -> None:
    lookup = {
        ("ACRELANDIA", "AC"): "1200013",
        ("ASSIS BRASIL", "AC"): "1200054",
    }
    body = Path("tests/fixtures/official-snapshots/tesouro-fundeb-por-municipio.csv").read_bytes()
    silver, quarantined = parse_tesouro_coint_municipio_csv(
        body,
        ibge_lookup=lookup,
        transfer_name="FUNDEB",
        competence="2025-01",
    )
    assert len(quarantined) == 1
    assert all(row["modality"] == "FUNDEB_RECEIVED" for row in silver)
    assert all(row["transferName"] == "FUNDEB" for row in silver)
    assert all(row["competence"] == "2025-01" for row in silver)
    assert {row["ibgeCode"] for row in silver} == {"1200013", "1200054"}
    assert sum(row["value"] for row in silver) == 1926974.37 + 1397435.94
    assert presentation_for("TESOURO-FUNDEB-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-FUNDEB-VALORES")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )


def test_tesouro_coint_cide_fex_wide_csv() -> None:
    lookup = {
        ("ACRELANDIA", "AC"): "1200013",
        ("ASSIS BRASIL", "AC"): "1200054",
    }
    cide_body = Path(
        "tests/fixtures/official-snapshots/tesouro-cide-por-municipio.csv"
    ).read_bytes()
    cide, cide_q = parse_tesouro_coint_municipio_csv(
        cide_body,
        ibge_lookup=lookup,
        transfer_name="CIDE",
        competence="2025-01",
    )
    assert len(cide_q) == 1
    assert all(row["modality"] == "CIDE_RECEIVED" for row in cide)
    assert all(row["transferName"] == "CIDE" for row in cide)
    assert all(row["competence"] == "2025-01" for row in cide)
    assert {row["ibgeCode"] for row in cide} == {"1200013", "1200054"}
    assert sum(row["value"] for row in cide) == 11707.50 + 6940.46
    assert presentation_for("TESOURO-CIDE-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-CIDE-VALORES")["valueKind"] == ("TRANSFER_AMOUNT_AS_PUBLISHED")
    fex_body = Path("tests/fixtures/official-snapshots/tesouro-fex-por-municipio.csv").read_bytes()
    fex, fex_q = parse_tesouro_coint_municipio_csv(
        fex_body,
        ibge_lookup=lookup,
        transfer_name="FEX",
        competence="2025-01",
    )
    assert len(fex_q) == 1
    assert all(row["modality"] == "FEX_RECEIVED" for row in fex)
    assert {row["ibgeCode"] for row in fex} == {"1200013", "1200054"}
    assert sum(row["value"] for row in fex) == 668.85 + 668.85
    assert presentation_for("TESOURO-FEX-VALORES")["createsTaxCredit"] is False
    assert presentation_for("TESOURO-FEX-VALORES")["valueKind"] == ("TRANSFER_AMOUNT_AS_PUBLISHED")


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
    ipi, quarantined_ipi = parse_state_pe_csv(body, tax="IPI", ibge_lookup=lookup)
    assert len(ipi) == 2
    abreu_ipi = next(row for row in ipi if row["ibgeCode"] == "2600054")
    assert abreu_ipi["value"] == 132.82
    assert abreu_ipi["modality"] == "IPI_QUOTA"
    recife_ipi = next(row for row in ipi if row["ibgeCode"] == "2611606")
    assert recife_ipi["value"] == 10.0
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-IPVA-QUOTA")["createsTaxCredit"] is False
    assert presentation_for("ESTADO-PE-IPI-QUOTA")["createsTaxCredit"] is False


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
    ipi, quarantined_ipi = parse_state_ba_csv(body, tax="IPI", ibge_lookup=lookup)
    assert len(ipi) == 2
    abaira_ipi = next(row for row in ipi if row["ibgeCode"] == "2900108")
    assert abaira_ipi["value"] == 2707.67
    assert abaira_ipi["modality"] == "IPI_QUOTA"
    alagoinhas_ipi = next(row for row in ipi if row["ibgeCode"] == "2900702")
    assert alagoinhas_ipi["value"] == 82490.23
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-BA-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-BA-IPVA-QUOTA")["createsTaxCredit"] is False
    assert presentation_for("ESTADO-BA-IPI-QUOTA")["createsTaxCredit"] is False


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
    ipi, quarantined_ipi = parse_state_mg_csv(
        body, tax="IPI", municipio_dim=municipio, tempo_dim=tempo
    )
    assert len(ipi) == 2
    abadia_ipi = next(row for row in ipi if row["ibgeCode"] == "3100104")
    assert abadia_ipi["value"] == 7602.47
    assert abadia_ipi["modality"] == "IPI_QUOTA"
    bh_ipi = next(row for row in ipi if row["ibgeCode"] == "3106200")
    assert bh_ipi["value"] == 899989.38
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-MG-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-MG-IPVA-QUOTA")["createsTaxCredit"] is False
    assert presentation_for("ESTADO-MG-IPI-QUOTA")["createsTaxCredit"] is False


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
    ipi, quarantined_ipi = parse_state_es_csv(body, tax="IPI")
    assert len(ipi) == 2
    afonso_ipi = next(row for row in ipi if row["ibgeCode"] == "3200102")
    assert afonso_ipi["value"] == 29837.91
    assert afonso_ipi["modality"] == "IPI_QUOTA"
    assert len(quarantined_ipi) == 1
    cide, quarantined_cide = parse_state_es_csv(body, tax="CIDE")
    assert len(cide) == 2
    vitoria_cide = next(row for row in cide if row["ibgeCode"] == "3205309")
    assert vitoria_cide["value"] == 109492.91
    assert vitoria_cide["modality"] == "CIDE_QUOTA"
    assert len(quarantined_cide) == 1
    assert presentation_for("ESTADO-ES-IPI-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-ES-CIDE-QUOTA")["createsTaxCredit"] is False
    frd, quarantined_frd = parse_state_es_csv(body, tax="FRD")
    assert len(frd) == 2
    vitoria_frd = next(row for row in frd if row["ibgeCode"] == "3205309")
    assert vitoria_frd["value"] == 942598.84
    assert vitoria_frd["modality"] == "FRD_QUOTA"
    assert len(quarantined_frd) == 1
    compensacao, quarantined_compensacao = parse_state_es_csv(body, tax="COMPENSACAO")
    assert len(compensacao) == 2
    afonso_comp = next(row for row in compensacao if row["ibgeCode"] == "3200102")
    assert afonso_comp["value"] == 21175.03
    assert afonso_comp["modality"] == "COMPENSACAO_QUOTA"
    assert len(quarantined_compensacao) == 1
    assert presentation_for("ESTADO-ES-FRD-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-ES-COMPENSACAO-QUOTA")["createsTaxCredit"] is False


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


def test_state_go_economia_xlsx_joins_name_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/go-economia-repasses-2024-11.xlsx").read_bytes()
    lookup = {
        ("ABADIA DE GOIAS", "GO"): "5200050",
        ("GOIANIA", "GO"): "5208707",
    }
    icms, quarantined = parse_state_go_economia_xlsx(
        body, tax="ICMS", competence="2024-11", ibge_lookup=lookup
    )
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"5200050", "5208707"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "GO" for row in icms)
    assert all(row["competence"] == "2024-11" for row in icms)
    abadia = next(row for row in icms if row["ibgeCode"] == "5200050")
    assert abadia["value"] == 800205.0
    goiania = next(row for row in icms if row["ibgeCode"] == "5208707")
    assert goiania["value"] == 12500000.0
    assert len(quarantined) == 1
    assert quarantined[0][1] == "missing IBGE municipality code"
    assert presentation_for("ESTADO-GO-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-GO-ICMS-QUOTA")["createsTaxCredit"] is False
    ipi, quarantined_ipi = parse_state_go_economia_xlsx(
        body, tax="IPI", competence="2024-11", ibge_lookup=lookup
    )
    assert len(ipi) == 2
    assert all(row["modality"] == "IPI_QUOTA" for row in ipi)
    abadia_ipi = next(row for row in ipi if row["ibgeCode"] == "5200050")
    assert abadia_ipi["value"] == 4405.34
    goiania_ipi = next(row for row in ipi if row["ibgeCode"] == "5208707")
    assert goiania_ipi["value"] == 1000.0
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-GO-IPI-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-GO-IPI-QUOTA")["createsTaxCredit"] is False


def test_state_ms_csv_joins_name_uf_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/ms-repasses-municipios-202601.csv").read_bytes()
    lookup = {
        ("AGUA CLARA", "MS"): "5000203",
        ("CAMPO GRANDE", "MS"): "5002704",
    }
    icms, quarantined_icms = parse_state_ms_csv(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"5000203", "5002704"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "MS" for row in icms)
    assert all(row["competence"] == "2026-01" for row in icms)
    agua = next(row for row in icms if row["ibgeCode"] == "5000203")
    assert agua["value"] == 4184093.08
    assert agua["territoryName"] == "AGUA CLARA"
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_ms_csv(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    campo = next(row for row in ipva if row["ibgeCode"] == "5002704")
    assert campo["value"] == 102601792.57
    assert campo["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-MS-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-MS-IPVA-QUOTA")["createsTaxCredit"] is False
    ipi, quarantined_ipi = parse_state_ms_csv(body, tax="IPI", ibge_lookup=lookup)
    assert len(ipi) == 2
    agua_ipi = next(row for row in ipi if row["ibgeCode"] == "5000203")
    assert agua_ipi["value"] == 57988.46
    assert agua_ipi["modality"] == "IPI_QUOTA"
    campo_ipi = next(row for row in ipi if row["ibgeCode"] == "5002704")
    assert campo_ipi["value"] == 605892.90
    assert len(quarantined_ipi) == 1
    cide, quarantined_cide = parse_state_ms_csv(body, tax="CIDE", ibge_lookup=lookup)
    assert len(cide) == 2
    agua_cide = next(row for row in cide if row["ibgeCode"] == "5000203")
    assert agua_cide["value"] == 15981.94
    assert agua_cide["modality"] == "CIDE_QUOTA"
    campo_cide = next(row for row in cide if row["ibgeCode"] == "5002704")
    assert campo_cide["value"] == 397118.34
    assert len(quarantined_cide) == 1
    assert presentation_for("ESTADO-MS-IPI-QUOTA")["createsTaxCredit"] is False
    assert presentation_for("ESTADO-MS-CIDE-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"


def test_state_ro_csv_joins_name_and_ibge6_and_quarantines_territory() -> None:
    icms_body = Path("tests/fixtures/official-snapshots/ro-icms-repasses-2022.csv").read_bytes()
    lookup = {
        ("PORTO VELHO", "RO"): "1100205",
        ("JI-PARANA", "RO"): "1100122",
    }
    icms, quarantined_icms = parse_state_ro_csv(icms_body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"1100205", "1100122"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "RO" for row in icms)
    assert all(row["competence"] == "2022-01" for row in icms)
    porto = next(row for row in icms if row["ibgeCode"] == "1100205")
    assert porto["value"] == 37300672.9
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva_body = Path("tests/fixtures/official-snapshots/ro-ipva-repasses-2022.csv").read_bytes()
    ipva, quarantined_ipva = parse_state_ro_csv(ipva_body, tax="IPVA")
    assert len(ipva) == 2
    ji = next(row for row in ipva if row["ibgeCode"] == "1100122")
    assert ji["value"] == 1723348.76
    porto_ipva = next(row for row in ipva if row["ibgeCode"] == "1100205")
    assert porto_ipva["value"] == 6079794.09
    assert porto_ipva["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-RO-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-RO-IPVA-QUOTA")["createsTaxCredit"] is False


def test_state_ac_csv_uses_native_ibge7_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/ac-icms-repasses-2021.csv").read_bytes()
    icms, quarantined = parse_state_ac_csv(body, tax="ICMS")
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"1200013", "1200054"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "AC" for row in icms)
    assert all(row["competence"] == "2021" for row in icms)
    acrelandia = next(row for row in icms if row["ibgeCode"] == "1200013")
    assert acrelandia["value"] == 4109661.0
    assis = next(row for row in icms if row["ibgeCode"] == "1200054")
    assert assis["value"] == 4416079.0
    assert len(quarantined) == 1
    assert quarantined[0][1] == "missing IBGE municipality code"
    assert presentation_for("ESTADO-AC-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-AC-ICMS-QUOTA")["createsTaxCredit"] is False


def test_state_ac_transparencia_json_joins_name_and_quarantines_territory() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/ac-transparencia-repasses-2025-01.json"
    ).read_bytes()
    lookup = {
        ("ACRELANDIA", "AC"): "1200013",
        ("ASSIS BRASIL", "AC"): "1200054",
    }
    ipva, quarantined = parse_state_ac_transparencia_json(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    assert {row["ibgeCode"] for row in ipva} == {"1200013", "1200054"}
    assert all(row["modality"] == "IPVA_QUOTA" for row in ipva)
    assert all(row["uf"] == "AC" for row in ipva)
    assert all(row["competence"] == "2025-01" for row in ipva)
    acrelandia = next(row for row in ipva if row["ibgeCode"] == "1200013")
    assert acrelandia["value"] == 119355.73
    assis = next(row for row in ipva if row["ibgeCode"] == "1200054")
    assert assis["value"] == 20042.59
    assert len(quarantined) == 1
    assert quarantined[0][1] == "missing IBGE municipality code"
    assert presentation_for("ESTADO-AC-IPVA-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-AC-IPVA-QUOTA")["createsTaxCredit"] is False
    icms, icms_q = parse_state_ac_transparencia_json(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    acrelandia_icms = next(row for row in icms if row["ibgeCode"] == "1200013")
    assert acrelandia_icms["value"] == 620540.98
    assert len(icms_q) == 1
    assert presentation_for("ESTADO-AC-ICMS-TRANSPARENCIA-QUOTA")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )
    assert presentation_for("ESTADO-AC-ICMS-TRANSPARENCIA-QUOTA")["createsTaxCredit"] is False
    fundeb, fundeb_q = parse_state_ac_transparencia_json(body, tax="FUNDEB", ibge_lookup=lookup)
    assert len(fundeb) == 2
    assert all(row["modality"] == "FUNDEB_QUOTA" for row in fundeb)
    acrelandia_fundeb = next(row for row in fundeb if row["ibgeCode"] == "1200013")
    assert acrelandia_fundeb["value"] == 155135.15
    assert len(fundeb_q) == 1
    assert presentation_for("ESTADO-AC-FUNDEB-TRANSPARENCIA-QUOTA")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )
    assert presentation_for("ESTADO-AC-FUNDEB-TRANSPARENCIA-QUOTA")["createsTaxCredit"] is False


def test_state_pi_repasseweb_html_aggregates_banks_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/pi-repasseweb-ipva-2025-01.html").read_bytes()
    lookup = {
        ("ACAUA", "PI"): "2200053",
        ("AGRICOLANDIA", "PI"): "2200103",
    }
    ipva, quarantined = parse_state_pi_repasseweb_html(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    assert {row["ibgeCode"] for row in ipva} == {"2200053", "2200103"}
    assert all(row["modality"] == "IPVA_QUOTA" for row in ipva)
    assert all(row["uf"] == "PI" for row in ipva)
    assert all(row["competence"] == "2025-01" for row in ipva)
    acaua = next(row for row in ipva if row["ibgeCode"] == "2200053")
    assert acaua["value"] == 103359.7
    agricolandia = next(row for row in ipva if row["ibgeCode"] == "2200103")
    assert agricolandia["value"] == 43613.82
    assert len(quarantined) == 1
    assert quarantined[0][1] == "missing IBGE municipality code"
    assert presentation_for("ESTADO-PI-IPVA-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-PI-IPVA-QUOTA")["createsTaxCredit"] is False


def test_state_rn_xls_joins_name_and_quarantines_territory() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/rn-repasses-prefeituras-2026-05.xls"
    ).read_bytes()
    lookup = {
        ("ACARI", "RN"): "2400109",
        ("NATAL", "RN"): "2408102",
    }
    icms, quarantined_icms = parse_state_rn_xls(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"2400109", "2408102"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "RN" for row in icms)
    assert all(row["competence"] == "2026-01" for row in icms)
    acari = next(row for row in icms if row["ibgeCode"] == "2400109")
    assert acari["value"] == 517463.75
    natal = next(row for row in icms if row["ibgeCode"] == "2408102")
    assert natal["value"] == 30427826.82
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_rn_xls(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    natal_ipva = next(row for row in ipva if row["ibgeCode"] == "2408102")
    assert natal_ipva["value"] == 6416335.88
    assert natal_ipva["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    ipi, quarantined_ipi = parse_state_rn_xls(body, tax="IPI", ibge_lookup=lookup)
    assert len(ipi) == 2
    natal_ipi = next(row for row in ipi if row["ibgeCode"] == "2408102")
    assert natal_ipi["value"] == 987654.32
    assert natal_ipi["modality"] == "IPI_QUOTA"
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-RN-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-RN-IPVA-QUOTA")["createsTaxCredit"] is False
    assert presentation_for("ESTADO-RN-IPI-QUOTA")["createsTaxCredit"] is False


def test_state_ma_xls_joins_name_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/ma-repasses-municipais-2026.xls").read_bytes()
    lookup = {
        ("ACAILANDIA", "MA"): "2100055",
        ("AFONSO CUNHA", "MA"): "2100154",
    }
    icms, quarantined_icms = parse_state_ma_xls(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"2100055", "2100154"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "MA" for row in icms)
    assert all(row["competence"] == "2026-01" for row in icms)
    acailandia = next(row for row in icms if row["ibgeCode"] == "2100055")
    assert acailandia["value"] == 10167145.37
    afonso = next(row for row in icms if row["ibgeCode"] == "2100154")
    assert afonso["value"] == 654767.6
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_ma_xls(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    acailandia_ipva = next(row for row in ipva if row["ibgeCode"] == "2100055")
    assert acailandia_ipva["value"] == 1083447.07
    assert acailandia_ipva["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 0
    assert presentation_for("ESTADO-MA-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-MA-IPVA-QUOTA")["createsTaxCredit"] is False
    ipi, quarantined_ipi = parse_state_ma_xls(body, tax="IPI", ibge_lookup=lookup)
    assert len(ipi) == 2
    acailandia_ipi = next(row for row in ipi if row["ibgeCode"] == "2100055")
    assert acailandia_ipi["value"] == 61876.21
    assert acailandia_ipi["modality"] == "IPI_QUOTA"
    afonso_ipi = next(row for row in ipi if row["ibgeCode"] == "2100154")
    assert afonso_ipi["value"] == 3984.85
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-MA-IPI-QUOTA")["createsTaxCredit"] is False


def test_state_pr_html_joins_name_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/pr-repasses-mensal-2025-01.html").read_bytes()
    lookup = {
        ("CASCAVEL", "PR"): "4104808",
        ("CURITIBA", "PR"): "4106902",
    }
    icms, quarantined_icms = parse_state_pr_html(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"4104808", "4106902"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "PR" for row in icms)
    assert all(row["competence"] == "2025-01" for row in icms)
    cascavel = next(row for row in icms if row["ibgeCode"] == "4104808")
    assert cascavel["value"] == 19375868.62
    curitiba = next(row for row in icms if row["ibgeCode"] == "4106902")
    assert curitiba["value"] == 76525586.35
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_pr_html(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    curitiba_ipva = next(row for row in ipva if row["ibgeCode"] == "4106902")
    assert curitiba_ipva["value"] == 353118489.28
    assert curitiba_ipva["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-PR-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-PR-IPVA-QUOTA")["createsTaxCredit"] is False
    ipi, quarantined_ipi = parse_state_pr_html(body, tax="IPI", ibge_lookup=lookup)
    assert len(ipi) == 2
    cascavel_ipi = next(row for row in ipi if row["ibgeCode"] == "4104808")
    assert cascavel_ipi["value"] == 225792.78
    assert cascavel_ipi["modality"] == "IPI_QUOTA"
    curitiba_ipi = next(row for row in ipi if row["ibgeCode"] == "4106902")
    assert curitiba_ipi["value"] == 891840.03
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-PR-IPI-QUOTA")["createsTaxCredit"] is False
    royalty, quarantined_royalty = parse_state_pr_html(body, tax="ROYALTY", ibge_lookup=lookup)
    assert len(royalty) == 2
    cascavel_royalty = next(row for row in royalty if row["ibgeCode"] == "4104808")
    assert cascavel_royalty["value"] == 17157.76
    assert cascavel_royalty["modality"] == "ROYALTY_QUOTA"
    curitiba_royalty = next(row for row in royalty if row["ibgeCode"] == "4106902")
    assert curitiba_royalty["value"] == 67769.98
    assert len(quarantined_royalty) == 1
    assert presentation_for("ESTADO-PR-ROYALTY-QUOTA")["createsTaxCredit"] is False


def test_state_pa_icms_verde_xlsx_joins_name_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/pa-icms-verde-2024-01.xlsx").read_bytes()
    lookup = {
        ("BELEM", "PA"): "1501402",
        ("ANANINDEUA", "PA"): "1500800",
    }
    silver, quarantined = parse_state_pa_icms_verde_xlsx(body, ibge_lookup=lookup)
    assert len(silver) == 2
    assert {row["ibgeCode"] for row in silver} == {"1501402", "1500800"}
    assert all(row["modality"] == "ICMS_VERDE_QUOTA" for row in silver)
    assert all(row["transferName"] == "ICMS_VERDE" for row in silver)
    assert all(row["uf"] == "PA" for row in silver)
    assert all(row["competence"] == "2024-01" for row in silver)
    belem = next(row for row in silver if row["ibgeCode"] == "1501402")
    assert belem["value"] == 126030.92
    ananindeua = next(row for row in silver if row["ibgeCode"] == "1500800")
    assert ananindeua["value"] == 58263.53
    assert len(quarantined) == 1
    assert quarantined[0][1] == "missing IBGE municipality code"
    assert presentation_for("ESTADO-PA-ICMS-VERDE-QUOTA")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )
    assert presentation_for("ESTADO-PA-ICMS-VERDE-QUOTA")["createsTaxCredit"] is False


def test_state_ce_xls_joins_name_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/ce-repasses-2025-01.xls").read_bytes()
    lookup = {
        ("ABAIARA", "CE"): "2300101",
        ("FORTALEZA", "CE"): "2304400",
    }
    icms, quarantined_icms = parse_state_ce_xls(body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"2300101", "2304400"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "CE" for row in icms)
    assert all(row["competence"] == "2025-01" for row in icms)
    abaiara = next(row for row in icms if row["ibgeCode"] == "2300101")
    assert abaiara["value"] == 757926.87
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_ce_xls(body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    fortaleza = next(row for row in ipva if row["ibgeCode"] == "2304400")
    assert fortaleza["value"] == 8000000.0
    assert fortaleza["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    ipi, quarantined_ipi = parse_state_ce_xls(body, tax="IPI", ibge_lookup=lookup)
    assert len(ipi) == 2
    abaiara_ipi = next(row for row in ipi if row["ibgeCode"] == "2300101")
    assert abaiara_ipi["value"] == 1200.5
    assert abaiara_ipi["modality"] == "IPI_QUOTA"
    fortaleza_ipi = next(row for row in ipi if row["ibgeCode"] == "2304400")
    assert fortaleza_ipi["value"] == 900000.0
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-CE-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-CE-IPVA-QUOTA")["createsTaxCredit"] is False
    assert presentation_for("ESTADO-CE-IPI-QUOTA")["createsTaxCredit"] is False


def test_state_rs_xls_joins_name_and_quarantines_territory() -> None:
    icms_body = Path("tests/fixtures/official-snapshots/rs-icms-repasses-2025-01.xls").read_bytes()
    ipva_body = Path("tests/fixtures/official-snapshots/rs-ipva-repasses-2025-01.xls").read_bytes()
    lookup = {
        ("ACEGUA", "RS"): "4300034",
        ("PORTO ALEGRE", "RS"): "4314902",
    }
    icms, quarantined_icms = parse_state_rs_xls(icms_body, tax="ICMS", ibge_lookup=lookup)
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"4300034", "4314902"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "RS" for row in icms)
    assert all(row["competence"] == "2025-01" for row in icms)
    acegua = next(row for row in icms if row["ibgeCode"] == "4300034")
    assert acegua["value"] == 1146019.89
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_rs_xls(ipva_body, tax="IPVA", ibge_lookup=lookup)
    assert len(ipva) == 2
    porto = next(row for row in ipva if row["ibgeCode"] == "4314902")
    assert porto["value"] == 8000000.0
    assert porto["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    assert presentation_for("ESTADO-RS-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-RS-IPVA-QUOTA")["createsTaxCredit"] is False
    compensacao_body = Path(
        "tests/fixtures/official-snapshots/rs-compensacao-lc194-2024-10.xls"
    ).read_bytes()
    compensacao, quarantined_comp = parse_state_rs_xls(
        compensacao_body,
        tax="COMPENSACAO_LC194",
        competence="2024-10",
        ibge_lookup=lookup,
    )
    assert len(compensacao) == 2
    assert {row["ibgeCode"] for row in compensacao} == {"4300034", "4314902"}
    assert all(row["modality"] == "COMPENSACAO_LC194_QUOTA" for row in compensacao)
    assert all(row["competence"] == "2024-10" for row in compensacao)
    acegua_comp = next(row for row in compensacao if row["ibgeCode"] == "4300034")
    assert acegua_comp["value"] == 194293.15
    assert len(quarantined_comp) == 1
    assert presentation_for("ESTADO-RS-COMPENSACAO-LC194-QUOTA")["valueKind"] == (
        "TRANSFER_AMOUNT_AS_PUBLISHED"
    )
    assert presentation_for("ESTADO-RS-COMPENSACAO-LC194-QUOTA")["createsTaxCredit"] is False


def test_state_al_xls_native_ibge_and_quarantines_territory() -> None:
    body = Path("tests/fixtures/official-snapshots/al-repasses-estaduais-2021.xls").read_bytes()
    icms, quarantined_icms = parse_state_al_xls(body, tax="ICMS", competence_year="2021")
    assert len(icms) == 2
    assert {row["ibgeCode"] for row in icms} == {"2700102", "2700300"}
    assert all(row["modality"] == "ICMS_QUOTA" for row in icms)
    assert all(row["uf"] == "AL" for row in icms)
    assert all(row["competence"] == "2021" for row in icms)
    agua = next(row for row in icms if row["ibgeCode"] == "2700102")
    assert agua["value"] == 3318269.81
    assert len(quarantined_icms) == 1
    assert quarantined_icms[0][1] == "missing IBGE municipality code"
    ipva, quarantined_ipva = parse_state_al_xls(body, tax="IPVA", competence_year="2021")
    assert len(ipva) == 2
    arapiraca = next(row for row in ipva if row["ibgeCode"] == "2700300")
    assert arapiraca["value"] == 8000000.0
    assert arapiraca["modality"] == "IPVA_QUOTA"
    assert len(quarantined_ipva) == 1
    ipi, quarantined_ipi = parse_state_al_xls(body, tax="IPI", competence_year="2021")
    assert len(ipi) == 2
    agua_ipi = next(row for row in ipi if row["ibgeCode"] == "2700102")
    assert agua_ipi["value"] == 1533.01
    assert agua_ipi["modality"] == "IPI_QUOTA"
    arapiraca_ipi = next(row for row in ipi if row["ibgeCode"] == "2700300")
    assert arapiraca_ipi["value"] == 23299.08
    assert len(quarantined_ipi) == 1
    assert presentation_for("ESTADO-AL-ICMS-QUOTA")["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert presentation_for("ESTADO-AL-IPVA-QUOTA")["createsTaxCredit"] is False
    assert presentation_for("ESTADO-AL-IPI-QUOTA")["createsTaxCredit"] is False
    royalty, quarantined_royalty = parse_state_al_xls(body, tax="ROYALTY", competence_year="2021")
    assert len(royalty) == 2
    agua_royalty = next(row for row in royalty if row["ibgeCode"] == "2700102")
    assert agua_royalty["value"] == 17942.32
    assert agua_royalty["modality"] == "ROYALTY_QUOTA"
    arapiraca_royalty = next(row for row in royalty if row["ibgeCode"] == "2700300")
    assert arapiraca_royalty["value"] == 323715.38
    assert len(quarantined_royalty) == 1
    assert presentation_for("ESTADO-AL-ROYALTY-QUOTA")["createsTaxCredit"] is False


def test_aneel_indqual_aggregates_by_ibge7() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/aneel-indqual-municipio-ms-limit8.json"
    ).read_bytes()
    silver, quarantined = parse_aneel_ckan_open(body, uf="MS")
    assert len(silver) == 6
    by_ibge = {row["ibgeCode"]: row for row in silver}
    assert by_ibge["5004700"]["value"] == 2
    assert by_ibge["5004700"]["unit"] == "CONSUMER_UNIT_SETS"
    assert by_ibge["5005806"]["value"] == 1
    assert len(quarantined) == 1
    assert quarantined[0][1] == "invalid IBGE municipality code"
    assert presentation_for("ANEEL-DADOS-ABERTOS")["valueKind"] == "REFERENCE_QUANTITY"
    assert presentation_for("ANEEL-DADOS-ABERTOS")["createsTaxCredit"] is False


def test_bcb_sgs_allowlist_parses_points() -> None:
    body = Path("tests/fixtures/official-snapshots/bcb-sgs-432-ultimos3.json").read_bytes()
    silver, quarantined = parse_bcb_sgs_olinda(
        body,
        series_id=432,
        series_label="SELIC_META",
        unit="PERCENT_PER_YEAR",
        allowlist=[432, 433],
    )
    assert len(silver) == 3
    assert quarantined == []
    assert silver[0]["transferName"] == "SELIC_META"
    assert silver[0]["value"] == 13.75
    assert silver[0]["unit"] == "PERCENT_PER_YEAR"
    assert silver[0]["seriesId"] == "432"
    assert silver[0]["uf"] == "BR"
    assert presentation_for("BCB-SGS-OLINDA")["valueKind"] == "REFERENCE_QUANTITY"
    assert presentation_for("BCB-SGS-OLINDA")["createsTaxCredit"] is False


def test_epe_anuario_parses_uf_year_scoped_consumers() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/epe-anuario-dados-brutos-ms-2024.csv"
    ).read_bytes()
    silver, quarantined = parse_epe_open_files(body, uf="MS", competence_year="2024", max_rows=8)
    assert len(silver) == 6
    assert len(quarantined) == 1
    assert quarantined[0][1] == "invalid consumer count"
    assert silver[0]["uf"] == "MS"
    assert silver[0]["competence"] == "2024-01"
    assert silver[0]["value"] == 38741
    assert silver[0]["unit"] == "CONSUMERS"
    assert silver[0]["transferName"] == "Residencial"
    assert all(row["uf"] == "MS" for row in silver)
    assert presentation_for("EPE-DADOS-ABERTOS")["valueKind"] == "REFERENCE_QUANTITY"
    assert presentation_for("EPE-DADOS-ABERTOS")["createsTaxCredit"] is False


def test_anatel_meu_municipio_parses_uf_ibge7_scoped_acessos() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/anatel-meu-municipio-acessos-ms-2025-11.csv"
    ).read_bytes()
    silver, quarantined = parse_anatel_dados_gov(
        body,
        uf="MS",
        competence_year="2025",
        competence_month="11",
        service="Banda Larga Fixa",
        max_rows=8,
    )
    assert len(silver) == 6
    assert len(quarantined) == 1
    assert quarantined[0][1] == "invalid IBGE municipality code"
    assert silver[0]["uf"] == "MS"
    assert silver[0]["ibgeCode"] == "5005251"
    assert silver[0]["competence"] == "2025-11"
    assert silver[0]["value"] == 296
    assert silver[0]["unit"] == "ACCESS_LINES"
    assert silver[0]["transferName"] == "ANATEL_BANDA_LARGA_FIXA_ACESSOS"
    assert all(row["uf"] == "MS" for row in silver)
    assert all(len(row["ibgeCode"]) == 7 for row in silver)
    assert presentation_for("ANATEL-DADOS-ABERTOS")["valueKind"] == "REFERENCE_QUANTITY"
    assert presentation_for("ANATEL-DADOS-ABERTOS")["createsTaxCredit"] is False


def test_cnes_demas_parses_uf_scoped_establishment_counts() -> None:
    body = Path(
        "tests/fixtures/official-snapshots/cnes-estabelecimentos-ms-limit8.json"
    ).read_bytes()
    silver, quarantined = parse_cnes_datasus_open(
        body,
        uf="MS",
        codigo_uf=50,
        competence="as_published",
        max_rows=8,
    )
    assert len(silver) == 5
    assert len(quarantined) == 1
    assert quarantined[0][1] == "invalid IBGE municipality code"
    assert silver[0]["uf"] == "MS"
    assert silver[0]["ibgeCode"] == "5000807"
    assert silver[0]["value"] == 1
    assert any(row["ibgeCode"] == "5002704" and row["value"] == 3 for row in silver)
    assert all(row["uf"] == "MS" for row in silver)
    assert all(len(row["ibgeCode"]) == 7 for row in silver)
    assert all(row["unit"] == "ESTABLISHMENTS" for row in silver)
    assert all(row["transferName"] == "CNES_ESTABELECIMENTOS" for row in silver)
    assert presentation_for("CNES-DATASUS")["valueKind"] == "REFERENCE_QUANTITY"
    assert presentation_for("CNES-DATASUS")["createsTaxCredit"] is False


def test_anp_revendedores_aggregates_and_drops_cnpj() -> None:
    body = Path("tests/fixtures/official-snapshots/anp-revendedores-ms-page1.json").read_bytes()
    lookup = {("CAMPO GRANDE", "MS"): "5002704"}
    silver, quarantined = parse_anp_revendedores_api(body, uf="MS", ibge_lookup=lookup)
    assert len(silver) == 1
    assert silver[0]["ibgeCode"] == "5002704"
    assert silver[0]["value"] == 2
    assert silver[0]["unit"] == "ESTABLISHMENTS"
    assert "cnpj" not in silver[0]
    assert "razaoSocial" not in silver[0]
    assert len(quarantined) == 1
    assert quarantined[0][1] == "missing IBGE municipality code"
    assert presentation_for("ANP-REVENDEDORES")["valueKind"] == "REFERENCE_QUANTITY"
    assert presentation_for("ANP-REVENDEDORES")["createsTaxCredit"] is False
