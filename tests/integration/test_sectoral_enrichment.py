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


def test_sectoral_enrichment_endpoint_partial_anp_aneel_bcb(api_client) -> None:
    response = api_client.get("/v1/sectoral-enrichment", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["ingestEnabled"] is True
    assert body["createsTaxCredit"] is False
    assert body["commandsDisabled"] is True
    assert body["items"] == []
    assert body["total"] == 0
    assert body["institutionalStatus"] == "PARTIAL_TECHNICAL_ACTIVATION"
    assert len(body["sources"]) == 6
    by_id = {row["sourceId"]: row for row in body["sources"]}
    assert by_id["ANP-REVENDEDORES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANP-REVENDEDORES"]["ingestAllowed"] is True
    assert by_id["ANEEL-DADOS-ABERTOS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ANEEL-DADOS-ABERTOS"]["ingestAllowed"] is True
    assert by_id["BCB-SGS-OLINDA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["BCB-SGS-OLINDA"]["ingestAllowed"] is True
    assert by_id["EPE-DADOS-ABERTOS"]["ingestAllowed"] is False


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


def test_anp_aneel_bcb_listed_and_other_sectorals_blocked(api_client) -> None:
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
    for source_id in (
        "EPE-DADOS-ABERTOS",
        "ANATEL-DADOS-ABERTOS",
        "CNES-DATASUS",
    ):
        assert by_id[source_id]["status"] == "DISCOVERED"
        assert by_id[source_id]["ingestAllowed"] is False
    blocked = api_client.post("/v1/data-sources/EPE-DADOS-ABERTOS/ingest", headers=_admin())
    assert blocked.status_code == 403


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
