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
    assert body["verifiedCount"] >= 4
    by_uf = {row["uf"]: row for row in body["states"]}
    assert by_uf["PE"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["PE"]["ingestAllowed"] is True
    assert by_uf["BA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["BA"]["ingestAllowed"] is True
    assert by_uf["MG"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["MG"]["ingestAllowed"] is True
    assert by_uf["ES"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["ES"]["ingestAllowed"] is True
    assert by_uf["GO"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["GO"]["ingestAllowed"] is True
    assert by_uf["GO"]["taxes"] == ["IPVA"]
    assert by_uf["MS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["MS"]["ingestAllowed"] is True
    assert by_uf["RO"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["RO"]["ingestAllowed"] is True
    assert by_uf["AC"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["AC"]["ingestAllowed"] is True
    assert by_uf["AC"]["taxes"] == ["ICMS", "IPVA"]
    assert by_uf["CE"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["CE"]["ingestAllowed"] is True
    assert by_uf["CE"]["taxes"] == ["ICMS", "IPVA", "IPI"]
    assert by_uf["RS"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["RS"]["ingestAllowed"] is True
    assert by_uf["RS"]["taxes"] == ["ICMS", "IPVA"]
    assert by_uf["PI"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["PI"]["ingestAllowed"] is True
    assert by_uf["PI"]["taxes"] == ["IPVA"]
    assert by_uf["SE"]["status"] == "PROVENANCE_VERIFIED"
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
    assert siconfi.json()["silverCount"] == 20
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
    assert siconfi.json()["silverCount"] == 20
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


def test_state_mg_ingest_publishes_gold_without_credit(api_client) -> None:
    icms = api_client.post("/v1/data-sources/ESTADO-MG-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-MG-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-MG-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MG-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-MG-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-MG-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 817661.12 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_es_ingest_publishes_gold_without_credit(api_client) -> None:
    icms = api_client.post("/v1/data-sources/ESTADO-ES-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-ES-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-ES-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-ES-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-ES-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-ES-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 3268119.24 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_go_ipva_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 20
    ipva = api_client.post("/v1/data-sources/ESTADO-GO-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-GO-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-GO-IPVA-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 13397.86 for item in lines.json()["items"])
    assert any(item["value"] == 3513965.9 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_ms_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 20
    icms = api_client.post("/v1/data-sources/ESTADO-MS-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-MS-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-MS-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MS-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-MS-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-MS-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 4184093.08 for item in lines.json()["items"])
    assert any(item["value"] == 43717529.34 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_ro_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 20
    icms = api_client.post("/v1/data-sources/ESTADO-RO-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-RO-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-RO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RO-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-RO-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-RO-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 37300672.9 for item in lines.json()["items"])
    assert any(item["value"] == 7813525.42 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_ac_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 20
    icms = api_client.post("/v1/data-sources/ESTADO-AC-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-AC-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-AC-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AC-ICMS-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-AC-ICMS-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    assert by_id["ESTADO-AC-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AC-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-AC-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-AC-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 4109661.0 for item in lines.json()["items"])
    assert any(item["value"] == 4416079.0 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )
    ipva_lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-AC-IPVA-QUOTA",
        headers=_analyst(),
    )
    assert ipva_lines.status_code == 200
    assert any(item["value"] == 119355.73 for item in ipva_lines.json()["items"])
    assert any(item["value"] == 20042.59 for item in ipva_lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in ipva_lines.json()["items"]
    )


def test_state_ce_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 20
    icms = api_client.post("/v1/data-sources/ESTADO-CE-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-CE-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-CE-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-CE-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-CE-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-CE-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 757926.87 for item in lines.json()["items"])
    assert any(item["value"] == 50000000.0 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_rs_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 20
    icms = api_client.post("/v1/data-sources/ESTADO-RS-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-RS-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-RS-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RS-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-RS-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-RS-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 1146019.89 for item in lines.json()["items"])
    assert any(item["value"] == 50000000.0 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_al_ingest_publishes_gold_without_credit(api_client) -> None:
    icms = api_client.post("/v1/data-sources/ESTADO-AL-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-AL-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-AL-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-AL-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-AL-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-AL-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 3318269.81 for item in lines.json()["items"])
    assert any(item["value"] == 50000000.0 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_pi_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 20
    ipva = api_client.post("/v1/data-sources/ESTADO-PI-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-PI-IPVA-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PI-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-PI-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-PI-IPVA-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 103359.7 for item in lines.json()["items"])
    assert any(item["value"] == 43613.82 for item in lines.json()["items"])
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
