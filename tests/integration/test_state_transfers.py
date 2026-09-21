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
    assert by_uf["ES"]["taxes"] == ["ICMS", "IPVA", "IPI", "CIDE"]
    assert by_uf["GO"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["GO"]["ingestAllowed"] is True
    assert by_uf["GO"]["taxes"] == ["ICMS", "IPVA", "IPI"]
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
    assert by_uf["MA"]["status"] == "TECHNICALLY_APPROVED"
    assert by_uf["MA"]["ingestAllowed"] is True
    assert by_uf["MA"]["taxes"] == ["ICMS", "IPVA"]
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
    assert siconfi.json()["silverCount"] == 28
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
    assert siconfi.json()["silverCount"] == 28
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
    ipi = api_client.post("/v1/data-sources/ESTADO-ES-IPI-QUOTA/ingest", headers=_admin())
    assert ipi.status_code == 200
    assert ipi.json()["silverCount"] == 2
    assert ipi.json()["taxCreditCreated"] is False
    cide = api_client.post("/v1/data-sources/ESTADO-ES-CIDE-QUOTA/ingest", headers=_admin())
    assert cide.status_code == 200
    assert cide.json()["silverCount"] == 2
    assert cide.json()["taxCreditCreated"] is False
    gold_ext = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_ext = {item["sourceId"]: item for item in gold_ext.json()["items"]}
    assert by_ext["ESTADO-ES-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_ext["ESTADO-ES-CIDE-QUOTA"]["createsTaxCredit"] is False
    ipi_lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-ES-IPI-QUOTA",
        headers=_analyst(),
    )
    assert any(item["value"] == 29837.91 for item in ipi_lines.json()["items"])
    cide_lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-ES-CIDE-QUOTA",
        headers=_analyst(),
    )
    assert any(item["value"] == 109492.91 for item in cide_lines.json()["items"])


def test_state_go_ipva_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
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


def test_state_go_icms_economia_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
    icms = api_client.post("/v1/data-sources/ESTADO-GO-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-GO-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-GO-ICMS-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-GO-ICMS-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-GO-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 800205.0 for item in lines.json()["items"])
    assert any(item["value"] == 12500000.0 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )
    ipi = api_client.post("/v1/data-sources/ESTADO-GO-IPI-QUOTA/ingest", headers=_admin())
    assert ipi.status_code == 200
    assert ipi.json()["silverCount"] == 2
    assert ipi.json()["quarantinedCount"] == 1
    assert ipi.json()["taxCreditCreated"] is False
    gold_ipi = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_ipi = {item["sourceId"]: item for item in gold_ipi.json()["items"]}
    assert by_ipi["ESTADO-GO-IPI-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_ipi["ESTADO-GO-IPI-QUOTA"]["createsTaxCredit"] is False
    ipi_lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-GO-IPI-QUOTA",
        headers=_analyst(),
    )
    assert any(item["value"] == 4405.34 for item in ipi_lines.json()["items"])
    assert any(item["value"] == 1000.0 for item in ipi_lines.json()["items"])


def test_state_ms_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
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
    assert siconfi.json()["silverCount"] == 28
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
    assert siconfi.json()["silverCount"] == 28
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
    assert siconfi.json()["silverCount"] == 28
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
    assert siconfi.json()["silverCount"] == 28
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
    assert siconfi.json()["silverCount"] == 28
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


def test_state_rn_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
    icms = api_client.post("/v1/data-sources/ESTADO-RN-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-RN-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-RN-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-RN-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-RN-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-RN-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 517463.75 for item in lines.json()["items"])
    assert any(item["value"] == 30427826.82 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_ma_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
    icms = api_client.post("/v1/data-sources/ESTADO-MA-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-MA-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 0
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-MA-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-MA-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-MA-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-MA-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 10167145.37 for item in lines.json()["items"])
    assert any(item["value"] == 654767.6 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_pr_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
    icms = api_client.post("/v1/data-sources/ESTADO-PR-ICMS-QUOTA/ingest", headers=_admin())
    assert icms.status_code == 200
    assert icms.json()["silverCount"] == 2
    assert icms.json()["quarantinedCount"] == 1
    assert icms.json()["taxCreditCreated"] is False
    ipva = api_client.post("/v1/data-sources/ESTADO-PR-IPVA-QUOTA/ingest", headers=_admin())
    assert ipva.status_code == 200
    assert ipva.json()["silverCount"] == 2
    assert ipva.json()["quarantinedCount"] == 1
    assert ipva.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-PR-ICMS-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PR-IPVA-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-PR-IPVA-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-PR-ICMS-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 19375868.62 for item in lines.json()["items"])
    assert any(item["value"] == 76525586.35 for item in lines.json()["items"])
    assert all(
        item["bronzeSha256"] and item["landingManifestPath"] and item["officialUrl"]
        for item in lines.json()["items"]
    )


def test_state_pa_icms_verde_ingest_publishes_gold_without_credit(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 28
    verde = api_client.post("/v1/data-sources/ESTADO-PA-ICMS-VERDE-QUOTA/ingest", headers=_admin())
    assert verde.status_code == 200
    assert verde.json()["silverCount"] == 2
    assert verde.json()["quarantinedCount"] == 1
    assert verde.json()["taxCreditCreated"] is False
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    by_id = {item["sourceId"]: item for item in gold.json()["items"]}
    assert by_id["ESTADO-PA-ICMS-VERDE-QUOTA"]["valueKind"] == "TRANSFER_AMOUNT_AS_PUBLISHED"
    assert by_id["ESTADO-PA-ICMS-VERDE-QUOTA"]["createsTaxCredit"] is False
    assert by_id["ESTADO-PA-ICMS-VERDE-QUOTA"]["homologationStatus"] == (
        "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    )
    lines = api_client.get(
        "/v1/indicators/official-gold/lines?sourceId=ESTADO-PA-ICMS-VERDE-QUOTA",
        headers=_analyst(),
    )
    assert lines.status_code == 200
    assert any(item["value"] == 126030.92 for item in lines.json()["items"])
    assert any(item["value"] == 58263.53 for item in lines.json()["items"])
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
