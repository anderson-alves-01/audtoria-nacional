from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
)


def _analyst() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _admin() -> dict[str, str]:
    return auth_headers(
        subject=USER_ADMIN_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_sectoral_enrichment_endpoint_partial_anp_aneel_bcb_epe_anatel_cnes(api_client) -> None:
    response = api_client.get("/v1/sectoral-enrichment", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["ingestEnabled"] is True
    assert body["createsTaxCredit"] is False
    assert body["commandsDisabled"] is True
    assert body["items"] == []
    assert body["total"] == 0
    assert body["institutionalStatus"] == "PARTIAL_TECHNICAL_ACTIVATION"
    assert len(body["sources"]) == 7
    by_id = {row["sourceId"]: row for row in body["sources"]}
    assert by_id["ANP-REVENDEDORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANP-REVENDEDORES"]["ingestAllowed"] is True
    assert by_id["ANEEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANEEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["BCB-SGS-OLINDA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-SGS-OLINDA"]["ingestAllowed"] is True
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["ingestAllowed"] is True
    assert by_id["EPE-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["EPE-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["ANATEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANATEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["CNES-DATASUS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["CNES-DATASUS"]["ingestAllowed"] is True


def test_sectoral_enrichment_command_is_rejected(api_client) -> None:
    response = api_client.post("/v1/sectoral-enrichment", headers=_analyst(), json={})
    assert response.status_code == 409
    detail = str(response.json().get("detail", response.json()))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_sectoral_enrichment(api_client) -> None:
    response = api_client.get(
        "/v1/sectoral-enrichment",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403


def test_anp_aneel_bcb_epe_anatel_cnes_listed_and_ingestible(api_client) -> None:
    listing = api_client.get("/v1/data-sources", headers=_analyst())
    by_id = {item["sourceId"]: item for item in listing.json()["items"]}
    assert by_id["ANP-REVENDEDORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANP-REVENDEDORES"]["ingestAllowed"] is True
    assert by_id["ANEEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANEEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["ANEEL-DADOS-ABERTOS"]["createsTaxCredit"] is False
    assert by_id["BCB-SGS-OLINDA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-SGS-OLINDA"]["ingestAllowed"] is True
    assert by_id["BCB-SGS-OLINDA"]["createsTaxCredit"] is False
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["ingestAllowed"] is True
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["createsTaxCredit"] is False
    assert by_id["EPE-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["EPE-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["EPE-DADOS-ABERTOS"]["createsTaxCredit"] is False
    assert by_id["ANATEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANATEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["ANATEL-DADOS-ABERTOS"]["createsTaxCredit"] is False
    assert by_id["CNES-DATASUS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["CNES-DATASUS"]["ingestAllowed"] is True
    assert by_id["CNES-DATASUS"]["createsTaxCredit"] is False


def test_anp_ingest_publishes_gold_without_credit_or_cnpj(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    anp = api_client.post("/v1/data-sources/ANP-REVENDEDORES/ingest", headers=_admin())
    assert anp.status_code == 200
    assert anp.json()["silverCount"] == 1
    assert anp.json()["quarantinedCount"] == 1
    assert anp.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ANP-REVENDEDORES"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["ANP-REVENDEDORES"]["createsTaxCredit"] is False
    assert by_id["ANP-REVENDEDORES"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ANP-REVENDEDORES",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 2 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )
    assert all("cnpj" not in (item.get("payload") or {}) for item in lines.json()["items"])


def test_aneel_ingest_publishes_gold_without_credit(api_client) -> None:
    aneel = api_client.post("/v1/data-sources/ANEEL-DADOS-ABERTOS/ingest", headers=_admin())
    assert aneel.status_code == 200
    assert aneel.json()["silverCount"] == 6
    assert aneel.json()["quarantinedCount"] == 1
    assert aneel.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ANEEL-DADOS-ABERTOS"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["ANEEL-DADOS-ABERTOS"]["createsTaxCredit"] is False
    assert by_id["ANEEL-DADOS-ABERTOS"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ANEEL-DADOS-ABERTOS",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 2 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_bcb_ingest_publishes_gold_without_credit(api_client) -> None:
    bcb = api_client.post("/v1/data-sources/BCB-SGS-OLINDA/ingest", headers=_admin())
    assert bcb.status_code == 200
    assert bcb.json()["silverCount"] == 6
    assert bcb.json()["quarantinedCount"] == 0
    assert bcb.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["BCB-SGS-OLINDA"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["BCB-SGS-OLINDA"]["createsTaxCredit"] is False
    assert by_id["BCB-SGS-OLINDA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=BCB-SGS-OLINDA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 13.75 for item in lines.json()["items"])
    assert any(item["value"] == -0.32 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_bcb_olinda_expectativas_ingest_publishes_gold_without_credit(api_client) -> None:
    bcb = api_client.post("/v1/data-sources/BCB-OLINDA-EXPECTATIVAS/ingest", headers=_admin())
    assert bcb.status_code == 200
    assert bcb.json()["silverCount"] == 192
    assert bcb.json()["quarantinedCount"] == 0
    assert bcb.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["createsTaxCredit"] is False
    assert by_id["BCB-OLINDA-EXPECTATIVAS"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=BCB-OLINDA-EXPECTATIVAS",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    values = {item["value"] for item in lines.json()["items"]}
    assert 4.9488 in values
    assert 13.5625 in values
    assert 5.2 in values
    assert 1.8564 in values
    assert 1.7 in values
    assert 2.5 in values
    assert 1.6 in values
    assert 4.833 in values
    assert 3.73 in values
    assert 3.34 in values
    assert -0.4 in values
    assert -60.85 in values
    assert -9.0 in values
    assert 83.4 in values
    assert 5.215 in values
    assert 80.0 in values
    assert 4.5661 in values
    assert 6.9302 in values
    assert 3.4641 in values
    assert 0.9 in values
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_epe_ingest_publishes_gold_without_credit(api_client) -> None:
    epe = api_client.post("/v1/data-sources/EPE-DADOS-ABERTOS/ingest", headers=_admin())
    assert epe.status_code == 200
    assert epe.json()["silverCount"] == 6
    assert epe.json()["quarantinedCount"] == 1
    assert epe.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["EPE-DADOS-ABERTOS"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["EPE-DADOS-ABERTOS"]["createsTaxCredit"] is False
    assert by_id["EPE-DADOS-ABERTOS"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=EPE-DADOS-ABERTOS",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 38741 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_anatel_ingest_publishes_gold_without_credit(api_client) -> None:
    anatel = api_client.post("/v1/data-sources/ANATEL-DADOS-ABERTOS/ingest", headers=_admin())
    assert anatel.status_code == 200
    assert anatel.json()["silverCount"] == 6
    assert anatel.json()["quarantinedCount"] == 1
    assert anatel.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ANATEL-DADOS-ABERTOS"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["ANATEL-DADOS-ABERTOS"]["createsTaxCredit"] is False
    assert by_id["ANATEL-DADOS-ABERTOS"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ANATEL-DADOS-ABERTOS",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 296 for item in lines.json()["items"])
    assert any(item["ibgeCode"] == "5005251" for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_cnes_ingest_publishes_gold_without_credit_or_pii(api_client) -> None:
    cnes = api_client.post("/v1/data-sources/CNES-DATASUS/ingest", headers=_admin())
    assert cnes.status_code == 200
    assert cnes.json()["silverCount"] == 5
    assert cnes.json()["quarantinedCount"] == 1
    assert cnes.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["CNES-DATASUS"]["valueKind"] == "REFERENCE_QUANTITY"
    assert by_id["CNES-DATASUS"]["createsTaxCredit"] is False
    assert by_id["CNES-DATASUS"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=CNES-DATASUS",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(
        item["value"] == 3 and item["ibgeCode"] == "5002704" for item in lines.json()["items"]
    )
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )
    assert all(
        "cnpj" not in str(item).lower() and "email" not in str(item).lower()
        for item in lines.json()["items"]
    )
