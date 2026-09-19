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


def test_state_transfers_endpoint_is_empty_shell(api_client) -> None:
    response = api_client.get("/v1/state-transfers", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["ingestEnabled"] is True
    assert body["createsTaxCredit"] is False
    assert body["commandsDisabled"] is True
    assert body["items"] == []
    assert body["total"] == 0
    assert body["verifiedCount"] >= 3
    by_uf = {row["uf"]: row for row in body["states"]}
    assert by_uf["PE"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["PE"]["ingestAllowed"] is True
    assert by_uf["BA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["BA"]["ingestAllowed"] is True
    assert by_uf["RJ"]["status"] == "PROVENANCE_VERIFIED"


def test_state_transfers_command_is_rejected(api_client) -> None:
    response = api_client.post("/v1/state-transfers", headers=_analyst(), json={})
    assert response.status_code == 409
    detail = str(response.json().get("detail", response.json()))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_state_transfers(api_client) -> None:
    response = api_client.get("/v1/state-transfers", headers=_admin())
    assert response.status_code == 403


def test_state_pe_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 6
    icms = api_client.post("/v1/data-sources/ESTADO-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-IPVA-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 0.0 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_ba_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 6
    icms = api_client.post("/v1/data-sources/ESTADO-BA-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-BA-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-BA-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-BA-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-BA-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-BA-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 374980.42 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_rfb_ingest_remains_blocked(api_client) -> None:
    listing = api_client.get("/v1/data-sources", headers=_analyst())
    by_id = {item["sourceId"]: item for item in listing.json()["items"]}
    assert by_id["ESTADO-ICMS-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["ESTADO-ICMS-QUOTA"]["ingestAllowed"] is True
    assert by_id["ESTADO-IPVA-QUOTA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_id["RFB-DADOS-ABERTOS"]["status"] == "READY_FOR_TERRITORIAL_SCOPE"
    assert by_id["RFB-DADOS-ABERTOS"]["ingestAllowed"] is False
    blocked = api_client.post("/v1/data-sources/RFB-DADOS-ABERTOS/ingest", headers=_admin())
    assert blocked.status_code == 403
