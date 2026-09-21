from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
)


def _admin() -> dict[str, str]:
    return auth_headers(
        subject=USER_ADMIN_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _analyst() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_official_gold_empty_until_ingest(api_client) -> None:
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    assert gold.status_code == 200
    body = gold.json()
    assert body["createsTaxCredit"] is False
    assert "HOMOLOGAÇÃO HUMANA PENDENTE" in body["banner"]
    assert any(item["sourceId"] == "ESTADO-ICMS-QUOTA" for item in body["emptySources"])


def test_siconfi_entes_and_ibge_pib_and_planalto_ingest(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
    assert siconfi.json()["quarantinedCount"] == 1
    pib = api_client.post("/v1/data-sources/IBGE-SIDRA-PIB/ingest", headers=_admin())
    assert pib.status_code == 200
    assert pib.json()["silverCount"] == 2
    assert pib.json()["quarantinedCount"] == 2
    cemp = api_client.post("/v1/data-sources/IBGE-SIDRA-CEMP/ingest", headers=_admin())
    assert cemp.status_code == 200
    assert cemp.json()["silverCount"] == 6
    assert cemp.json()["quarantinedCount"] == 0
    assert cemp.json()["taxCreditCreated"] is False
    planalto = api_client.post("/v1/data-sources/PLANALTO-LEGISLACAO/ingest", headers=_admin())
    assert planalto.status_code == 200
    assert planalto.json()["silverCount"] == 1
    lc214 = api_client.post("/v1/data-sources/PLANALTO-LC-214/ingest", headers=_admin())
    assert lc214.status_code == 200
    assert lc214.json()["silverCount"] == 1
    fpm = api_client.post("/v1/data-sources/TESOURO-FPM-VALORES/ingest", headers=_admin())
    assert fpm.status_code == 200
    assert fpm.json()["silverCount"] == 3
    itr = api_client.post("/v1/data-sources/TESOURO-ITR-VALORES/ingest", headers=_admin())
    assert itr.status_code == 200
    assert itr.json()["silverCount"] == 3
    assert itr.json()["taxCreditCreated"] is False
    ipi_exp = api_client.post("/v1/data-sources/TESOURO-IPI-EXP-VALORES/ingest", headers=_admin())
    assert ipi_exp.status_code == 200
    assert ipi_exp.json()["silverCount"] == 2
    royalties = api_client.post(
        "/v1/data-sources/TESOURO-ROYALTIES-VALORES/ingest", headers=_admin()
    )
    assert royalties.status_code == 200
    assert royalties.json()["silverCount"] == 3
    assert royalties.json()["taxCreditCreated"] is False
    lc176 = api_client.post("/v1/data-sources/TESOURO-LC176-VALORES/ingest", headers=_admin())
    assert lc176.status_code == 200
    assert lc176.json()["silverCount"] == 2
    assert lc176.json()["taxCreditCreated"] is False
    iof = api_client.post("/v1/data-sources/TESOURO-IOF-OURO-VALORES/ingest", headers=_admin())
    assert iof.status_code == 200
    assert iof.json()["silverCount"] == 2
    assert iof.json()["taxCreditCreated"] is False
    cide = api_client.post("/v1/data-sources/TESOURO-CIDE-VALORES/ingest", headers=_admin())
    assert cide.status_code == 200
    assert cide.json()["silverCount"] == 2
    assert cide.json()["taxCreditCreated"] is False
    fex = api_client.post("/v1/data-sources/TESOURO-FEX-VALORES/ingest", headers=_admin())
    assert fex.status_code == 200
    assert fex.json()["silverCount"] == 2
    assert fex.json()["taxCreditCreated"] is False
    pe_icms = api_client.post("/v1/data-sources/ESTADO-ICMS-QUOTA/ingest", headers=_admin())
    assert pe_icms.status_code == 200
    assert pe_icms.json()["silverCount"] == 2
    pe_ipva = api_client.post("/v1/data-sources/ESTADO-IPVA-QUOTA/ingest", headers=_admin())
    assert pe_ipva.status_code == 200
    assert pe_ipva.json()["silverCount"] == 2
    pe_ipi = api_client.post("/v1/data-sources/ESTADO-PE-IPI-QUOTA/ingest", headers=_admin())
    assert pe_ipi.status_code == 200
    assert pe_ipi.json()["silverCount"] == 2
    ba_icms = api_client.post("/v1/data-sources/ESTADO-BA-ICMS-QUOTA/ingest", headers=_admin())
    assert ba_icms.status_code == 200
    assert ba_icms.json()["silverCount"] == 2
    ba_ipva = api_client.post("/v1/data-sources/ESTADO-BA-IPVA-QUOTA/ingest", headers=_admin())
    assert ba_ipva.status_code == 200
    assert ba_ipva.json()["silverCount"] == 2
    ba_ipi = api_client.post("/v1/data-sources/ESTADO-BA-IPI-QUOTA/ingest", headers=_admin())
    assert ba_ipi.status_code == 200
    assert ba_ipi.json()["silverCount"] == 2
    mg_icms = api_client.post("/v1/data-sources/ESTADO-MG-ICMS-QUOTA/ingest", headers=_admin())
    assert mg_icms.status_code == 200
    assert mg_icms.json()["silverCount"] == 2
    mg_ipva = api_client.post("/v1/data-sources/ESTADO-MG-IPVA-QUOTA/ingest", headers=_admin())
    assert mg_ipva.status_code == 200
    assert mg_ipva.json()["silverCount"] == 2
    mg_ipi = api_client.post("/v1/data-sources/ESTADO-MG-IPI-QUOTA/ingest", headers=_admin())
    assert mg_ipi.status_code == 200
    assert mg_ipi.json()["silverCount"] == 2
    es_icms = api_client.post("/v1/data-sources/ESTADO-ES-ICMS-QUOTA/ingest", headers=_admin())
    assert es_icms.status_code == 200
    assert es_icms.json()["silverCount"] == 2
    es_ipva = api_client.post("/v1/data-sources/ESTADO-ES-IPVA-QUOTA/ingest", headers=_admin())
    assert es_ipva.status_code == 200
    assert es_ipva.json()["silverCount"] == 2
    go_ipva = api_client.post("/v1/data-sources/ESTADO-GO-IPVA-QUOTA/ingest", headers=_admin())
    assert go_ipva.status_code == 200
    assert go_ipva.json()["silverCount"] == 2
    go_icms = api_client.post("/v1/data-sources/ESTADO-GO-ICMS-QUOTA/ingest", headers=_admin())
    assert go_icms.status_code == 200
    assert go_icms.json()["silverCount"] == 2
    assert go_icms.json()["quarantinedCount"] == 1
    go_ipi = api_client.post("/v1/data-sources/ESTADO-GO-IPI-QUOTA/ingest", headers=_admin())
    assert go_ipi.status_code == 200
    assert go_ipi.json()["silverCount"] == 2
    es_ipi = api_client.post("/v1/data-sources/ESTADO-ES-IPI-QUOTA/ingest", headers=_admin())
    assert es_ipi.status_code == 200
    assert es_ipi.json()["silverCount"] == 2
    es_cide = api_client.post("/v1/data-sources/ESTADO-ES-CIDE-QUOTA/ingest", headers=_admin())
    assert es_cide.status_code == 200
    assert es_cide.json()["silverCount"] == 2
    ms_icms = api_client.post("/v1/data-sources/ESTADO-MS-ICMS-QUOTA/ingest", headers=_admin())
    assert ms_icms.status_code == 200
    assert ms_icms.json()["silverCount"] == 2
    ms_ipva = api_client.post("/v1/data-sources/ESTADO-MS-IPVA-QUOTA/ingest", headers=_admin())
    assert ms_ipva.status_code == 200
    assert ms_ipva.json()["silverCount"] == 2
    ro_icms = api_client.post("/v1/data-sources/ESTADO-RO-ICMS-QUOTA/ingest", headers=_admin())
    assert ro_icms.status_code == 200
    assert ro_icms.json()["silverCount"] == 2
    ro_ipva = api_client.post("/v1/data-sources/ESTADO-RO-IPVA-QUOTA/ingest", headers=_admin())
    assert ro_ipva.status_code == 200
    assert ro_ipva.json()["silverCount"] == 2
    ac_icms = api_client.post("/v1/data-sources/ESTADO-AC-ICMS-QUOTA/ingest", headers=_admin())
    assert ac_icms.status_code == 200
    assert ac_icms.json()["silverCount"] == 2
    ac_ipva = api_client.post("/v1/data-sources/ESTADO-AC-IPVA-QUOTA/ingest", headers=_admin())
    assert ac_ipva.status_code == 200
    assert ac_ipva.json()["silverCount"] == 2
    ce_icms = api_client.post("/v1/data-sources/ESTADO-CE-ICMS-QUOTA/ingest", headers=_admin())
    assert ce_icms.status_code == 200
    assert ce_icms.json()["silverCount"] == 2
    ce_ipva = api_client.post("/v1/data-sources/ESTADO-CE-IPVA-QUOTA/ingest", headers=_admin())
    assert ce_ipva.status_code == 200
    assert ce_ipva.json()["silverCount"] == 2
    ce_ipi = api_client.post("/v1/data-sources/ESTADO-CE-IPI-QUOTA/ingest", headers=_admin())
    assert ce_ipi.status_code == 200
    assert ce_ipi.json()["silverCount"] == 2
    rs_icms = api_client.post("/v1/data-sources/ESTADO-RS-ICMS-QUOTA/ingest", headers=_admin())
    assert rs_icms.status_code == 200
    assert rs_icms.json()["silverCount"] == 2
    rs_ipva = api_client.post("/v1/data-sources/ESTADO-RS-IPVA-QUOTA/ingest", headers=_admin())
    assert rs_ipva.status_code == 200
    assert rs_ipva.json()["silverCount"] == 2
    al_icms = api_client.post("/v1/data-sources/ESTADO-AL-ICMS-QUOTA/ingest", headers=_admin())
    assert al_icms.status_code == 200
    assert al_icms.json()["silverCount"] == 2
    al_ipva = api_client.post("/v1/data-sources/ESTADO-AL-IPVA-QUOTA/ingest", headers=_admin())
    assert al_ipva.status_code == 200
    assert al_ipva.json()["silverCount"] == 2
    al_ipi = api_client.post("/v1/data-sources/ESTADO-AL-IPI-QUOTA/ingest", headers=_admin())
    assert al_ipi.status_code == 200
    assert al_ipi.json()["silverCount"] == 2
    pi_ipva = api_client.post("/v1/data-sources/ESTADO-PI-IPVA-QUOTA/ingest", headers=_admin())
    assert pi_ipva.status_code == 200
    assert pi_ipva.json()["silverCount"] == 2
    rn_icms = api_client.post("/v1/data-sources/ESTADO-RN-ICMS-QUOTA/ingest", headers=_admin())
    assert rn_icms.status_code == 200
    assert rn_icms.json()["silverCount"] == 2
    rn_ipva = api_client.post("/v1/data-sources/ESTADO-RN-IPVA-QUOTA/ingest", headers=_admin())
    assert rn_ipva.status_code == 200
    assert rn_ipva.json()["silverCount"] == 2
    rn_ipi = api_client.post("/v1/data-sources/ESTADO-RN-IPI-QUOTA/ingest", headers=_admin())
    assert rn_ipi.status_code == 200
    assert rn_ipi.json()["silverCount"] == 2
    ma_icms = api_client.post("/v1/data-sources/ESTADO-MA-ICMS-QUOTA/ingest", headers=_admin())
    assert ma_icms.status_code == 200
    assert ma_icms.json()["silverCount"] == 2
    ma_ipva = api_client.post("/v1/data-sources/ESTADO-MA-IPVA-QUOTA/ingest", headers=_admin())
    assert ma_ipva.status_code == 200
    assert ma_ipva.json()["silverCount"] == 2
    pr_icms = api_client.post("/v1/data-sources/ESTADO-PR-ICMS-QUOTA/ingest", headers=_admin())
    assert pr_icms.status_code == 200
    assert pr_icms.json()["silverCount"] == 2
    pr_ipva = api_client.post("/v1/data-sources/ESTADO-PR-IPVA-QUOTA/ingest", headers=_admin())
    assert pr_ipva.status_code == 200
    assert pr_ipva.json()["silverCount"] == 2
    pa_verde = api_client.post(
        "/v1/data-sources/ESTADO-PA-ICMS-VERDE-QUOTA/ingest", headers=_admin()
    )
    assert pa_verde.status_code == 200
    assert pa_verde.json()["silverCount"] == 2
    assert pa_verde.json()["quarantinedCount"] == 1
    rreo = api_client.post("/v1/data-sources/SICONFI-RREO/ingest", headers=_admin())
    assert rreo.status_code == 200
    assert rreo.json()["silverCount"] >= 1
    assert rreo.json()["taxCreditCreated"] is False
    dca = api_client.post("/v1/data-sources/SICONFI-DCA/ingest", headers=_admin())
    assert dca.status_code == 200
    assert dca.json()["silverCount"] >= 1
    assert dca.json()["taxCreditCreated"] is False
    rgf = api_client.post("/v1/data-sources/SICONFI-RGF/ingest", headers=_admin())
    assert rgf.status_code == 200
    assert rgf.json()["silverCount"] >= 1
    assert rgf.json()["taxCreditCreated"] is False
    blocked = api_client.post("/v1/data-sources/RFB-DADOS-ABERTOS/ingest", headers=_admin())
    assert blocked.status_code == 403
    portal = api_client.post(
        "/v1/data-sources/PORTAL-TRANSPARENCIA-TRANSFERENCIAS/ingest", headers=_admin()
    )
    assert portal.status_code == 403
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    body = gold.json()
    assert body["published"] is True
    by_id = {item["sourceId"]: item for item in body["items"]}
    expected = {
        "SICONFI-ENTES",
        "IBGE-SIDRA-PIB",
        "IBGE-SIDRA-CEMP",
        "PLANALTO-LEGISLACAO",
        "PLANALTO-LC-214",
        "TESOURO-FPM-VALORES",
        "TESOURO-ITR-VALORES",
        "TESOURO-IPI-EXP-VALORES",
        "TESOURO-ROYALTIES-VALORES",
        "TESOURO-LC176-VALORES",
        "TESOURO-IOF-OURO-VALORES",
        "TESOURO-CIDE-VALORES",
        "TESOURO-FEX-VALORES",
        "ESTADO-ICMS-QUOTA",
        "ESTADO-IPVA-QUOTA",
        "ESTADO-PE-IPI-QUOTA",
        "ESTADO-BA-ICMS-QUOTA",
        "ESTADO-BA-IPVA-QUOTA",
        "ESTADO-BA-IPI-QUOTA",
        "ESTADO-MG-ICMS-QUOTA",
        "ESTADO-MG-IPVA-QUOTA",
        "ESTADO-MG-IPI-QUOTA",
        "ESTADO-ES-ICMS-QUOTA",
        "ESTADO-ES-IPVA-QUOTA",
        "ESTADO-ES-IPI-QUOTA",
        "ESTADO-ES-CIDE-QUOTA",
        "ESTADO-GO-IPVA-QUOTA",
        "ESTADO-GO-ICMS-QUOTA",
        "ESTADO-GO-IPI-QUOTA",
        "ESTADO-MS-ICMS-QUOTA",
        "ESTADO-MS-IPVA-QUOTA",
        "ESTADO-RO-ICMS-QUOTA",
        "ESTADO-RO-IPVA-QUOTA",
        "ESTADO-AC-ICMS-QUOTA",
        "ESTADO-AC-IPVA-QUOTA",
        "ESTADO-CE-ICMS-QUOTA",
        "ESTADO-CE-IPVA-QUOTA",
        "ESTADO-CE-IPI-QUOTA",
        "ESTADO-RS-ICMS-QUOTA",
        "ESTADO-RS-IPVA-QUOTA",
        "ESTADO-AL-ICMS-QUOTA",
        "ESTADO-AL-IPVA-QUOTA",
        "ESTADO-AL-IPI-QUOTA",
        "ESTADO-PI-IPVA-QUOTA",
        "ESTADO-RN-ICMS-QUOTA",
        "ESTADO-RN-IPVA-QUOTA",
        "ESTADO-RN-IPI-QUOTA",
        "ESTADO-MA-ICMS-QUOTA",
        "ESTADO-MA-IPVA-QUOTA",
        "ESTADO-PR-ICMS-QUOTA",
        "ESTADO-PR-IPVA-QUOTA",
        "ESTADO-PA-ICMS-VERDE-QUOTA",
        "SICONFI-RREO",
        "SICONFI-DCA",
        "SICONFI-RGF",
    }
    assert expected <= set(by_id)
    assert by_id["IBGE-SIDRA-CEMP"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["PLANALTO-LC-214"]["valueKind"] == "REGULATORY_DOCUMENT"
    assert by_id["SICONFI-ENTES"]["valueKind"] == "COVERAGE_REGISTRY"
    assert by_id["TESOURO-FPM-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["TESOURO-ITR-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["TESOURO-IPI-EXP-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["TESOURO-ROYALTIES-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["TESOURO-LC176-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["TESOURO-IOF-OURO-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["TESOURO-CIDE-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["TESOURO-FEX-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PE-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-BA-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-BA-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-BA-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MG-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MG-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MG-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ES-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ES-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ES-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ES-CIDE-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-GO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-GO-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MS-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MS-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RO-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AC-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AC-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-CE-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-CE-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-CE-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RS-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RS-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AL-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AL-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AL-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PI-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RN-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RN-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RN-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MA-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MA-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PR-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PR-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PA-ICMS-VERDE-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["SICONFI-RREO"]["valueKind"] == "FISCAL_STATEMENT_LINE"
    assert by_id["SICONFI-DCA"]["valueKind"] == "FISCAL_STATEMENT_LINE"
    assert by_id["SICONFI-RGF"]["valueKind"] == "FISCAL_STATEMENT_LINE"
    assert all(
        item["homologationStatus"] == "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
        for item in body["items"]
    )
    assert all(item["createsTaxCredit"] is False for item in body["items"])
    lines = api_client.get("/v1/indicators/official-gold/lines", headers=_analyst())
    assert lines.status_code == 200
    assert lines.json()["items"]
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] for item in lines.json()["items"]
    )


def test_unavailable_sources_stay_empty(api_client) -> None:
    listing = api_client.get("/v1/data-sources", headers=_analyst())
    by_id = {item["sourceId"]: item for item in listing.json()["items"]}
    assert by_id["TESOURO-FPM-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-ITR-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-ITR-VALORES"]["ingestAllowed"] is True
    assert by_id["TESOURO-IPI-EXP-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-IPI-EXP-VALORES"]["ingestAllowed"] is True
    assert by_id["TESOURO-ROYALTIES-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-ROYALTIES-VALORES"]["ingestAllowed"] is True
    assert by_id["TESOURO-LC176-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-LC176-VALORES"]["ingestAllowed"] is True
    assert by_id["TESOURO-IOF-OURO-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-IOF-OURO-VALORES"]["ingestAllowed"] is True
    assert by_id["TESOURO-CIDE-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-CIDE-VALORES"]["ingestAllowed"] is True
    assert by_id["TESOURO-FEX-VALORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["TESOURO-FEX-VALORES"]["ingestAllowed"] is True
    assert by_id["ESTADO-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-PE-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-PE-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-BA-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-BA-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-BA-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-BA-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-BA-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-MG-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MG-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MG-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MG-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-MG-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-ES-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ES-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ES-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ES-CIDE-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ES-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-ES-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-GO-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-GO-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-GO-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-GO-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-MS-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MS-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MS-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-RO-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RO-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RO-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-AC-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-AC-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-AC-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-AC-IPVA-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-CE-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-CE-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-CE-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-CE-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-CE-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-RS-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RS-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RS-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-AL-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-AL-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-AL-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-AL-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-AL-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-PI-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-PI-IPVA-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-RN-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RN-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RN-IPI-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RN-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-RN-IPI-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-MA-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MA-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MA-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-PR-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-PR-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-PR-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-PA-ICMS-VERDE-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-PA-ICMS-VERDE-QUOTA"]["ingestAllowed"] is True
    assert by_id["ANP-REVENDEDORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANP-REVENDEDORES"]["ingestAllowed"] is True
    assert by_id["ANEEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANEEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["BCB-SGS-OLINDA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-SGS-OLINDA"]["ingestAllowed"] is True
    assert by_id["EPE-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["EPE-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["ANATEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANATEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["CNES-DATASUS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["CNES-DATASUS"]["ingestAllowed"] is True
    assert by_id["RFB-DADOS-ABERTOS"]["status"] == "READY_FOR_TERRITORIAL_SCOPE"
    assert by_id["RFB-DADOS-ABERTOS"]["ingestAllowed"] is False
    assert by_id["MUNICIPAL-IPTU-RESTRICTED"]["status"] == "CREDENTIAL_REQUIRED"
    assert by_id["PORTAL-TRANSPARENCIA-TRANSFERENCIAS"]["status"] == "CREDENTIAL_REQUIRED"
    assert by_id["PORTAL-TRANSPARENCIA-TRANSFERENCIAS"]["ingestAllowed"] is False
    assert by_id["PLANALTO-LC-214"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["PLANALTO-LC-214"]["ingestAllowed"] is True
    assert by_id["SICONFI-RGF"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["SICONFI-RGF"]["ingestAllowed"] is True
