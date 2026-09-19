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
    assert siconfi.json()["silverCount"] == 12
    assert siconfi.json()["quarantinedCount"] == 1
    pib = api_client.post("/v1/data-sources/IBGE-SIDRA-PIB/ingest", headers=_admin())
    assert pib.status_code == 200
    assert pib.json()["silverCount"] == 2
    assert pib.json()["quarantinedCount"] == 2
    planalto = api_client.post("/v1/data-sources/PLANALTO-LEGISLACAO/ingest", headers=_admin())
    assert planalto.status_code == 200
    assert planalto.json()["silverCount"] == 1
    lc214 = api_client.post("/v1/data-sources/PLANALTO-LC-214/ingest", headers=_admin())
    assert lc214.status_code == 200
    assert lc214.json()["silverCount"] == 1
    fpm = api_client.post("/v1/data-sources/TESOURO-FPM-VALORES/ingest", headers=_admin())
    assert fpm.status_code == 200
    assert fpm.json()["silverCount"] == 3
    pe_icms = api_client.post("/v1/data-sources/ESTADO-ICMS-QUOTA/ingest", headers=_admin())
    assert pe_icms.status_code == 200
    assert pe_icms.json()["silverCount"] == 2
    pe_ipva = api_client.post("/v1/data-sources/ESTADO-IPVA-QUOTA/ingest", headers=_admin())
    assert pe_ipva.status_code == 200
    assert pe_ipva.json()["silverCount"] == 2
    ba_icms = api_client.post("/v1/data-sources/ESTADO-BA-ICMS-QUOTA/ingest", headers=_admin())
    assert ba_icms.status_code == 200
    assert ba_icms.json()["silverCount"] == 2
    ba_ipva = api_client.post("/v1/data-sources/ESTADO-BA-IPVA-QUOTA/ingest", headers=_admin())
    assert ba_ipva.status_code == 200
    assert ba_ipva.json()["silverCount"] == 2
    mg_icms = api_client.post("/v1/data-sources/ESTADO-MG-ICMS-QUOTA/ingest", headers=_admin())
    assert mg_icms.status_code == 200
    assert mg_icms.json()["silverCount"] == 2
    mg_ipva = api_client.post("/v1/data-sources/ESTADO-MG-IPVA-QUOTA/ingest", headers=_admin())
    assert mg_ipva.status_code == 200
    assert mg_ipva.json()["silverCount"] == 2
    es_icms = api_client.post("/v1/data-sources/ESTADO-ES-ICMS-QUOTA/ingest", headers=_admin())
    assert es_icms.status_code == 200
    assert es_icms.json()["silverCount"] == 2
    es_ipva = api_client.post("/v1/data-sources/ESTADO-ES-IPVA-QUOTA/ingest", headers=_admin())
    assert es_ipva.status_code == 200
    assert es_ipva.json()["silverCount"] == 2
    go_ipva = api_client.post("/v1/data-sources/ESTADO-GO-IPVA-QUOTA/ingest", headers=_admin())
    assert go_ipva.status_code == 200
    assert go_ipva.json()["silverCount"] == 2
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
        "PLANALTO-LEGISLACAO",
        "PLANALTO-LC-214",
        "TESOURO-FPM-VALORES",
        "ESTADO-ICMS-QUOTA",
        "ESTADO-IPVA-QUOTA",
        "ESTADO-BA-ICMS-QUOTA",
        "ESTADO-BA-IPVA-QUOTA",
        "ESTADO-MG-ICMS-QUOTA",
        "ESTADO-MG-IPVA-QUOTA",
        "ESTADO-ES-ICMS-QUOTA",
        "ESTADO-ES-IPVA-QUOTA",
        "ESTADO-GO-IPVA-QUOTA",
        "ESTADO-MS-ICMS-QUOTA",
        "ESTADO-MS-IPVA-QUOTA",
        "ESTADO-RO-ICMS-QUOTA",
        "ESTADO-RO-IPVA-QUOTA",
        "SICONFI-RREO",
        "SICONFI-DCA",
        "SICONFI-RGF",
    }
    assert expected <= set(by_id)
    assert by_id["PLANALTO-LC-214"]["valueKind"] == "REGULATORY_DOCUMENT"
    assert by_id["SICONFI-ENTES"]["valueKind"] == "COVERAGE_REGISTRY"
    assert by_id["TESOURO-FPM-VALORES"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-BA-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-BA-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MG-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MG-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ES-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ES-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MS-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MS-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RO-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
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
    assert by_id["ESTADO-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-BA-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-BA-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-BA-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-MG-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MG-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MG-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-ES-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ES-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ES-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-MS-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MS-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-MS-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-RO-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RO-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-RO-ICMS-QUOTA"]["ingestAllowed"] is True
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
