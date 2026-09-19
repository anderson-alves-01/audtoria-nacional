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
    assert body["ingestEnabled"] is False
    assert body["createsTaxCredit"] is False
    assert body["commandsDisabled"] is True
    assert body["items"] == []
    assert body["total"] == 0
    assert body["verifiedCount"] >= 1
    by_uf = {row["uf"]: row for row in body["states"]}
    assert by_uf["RJ"]["status"] == "PROVENANCE_VERIFIED"
    assert by_uf["RJ"]["ingestAllowed"] is False


def test_state_transfers_command_is_rejected(api_client) -> None:
    response = api_client.post("/v1/state-transfers", headers=_analyst(), json={})
    assert response.status_code == 409
    detail = str(response.json().get("detail", response.json()))
    assert "desativad" in detail.lower()


def test_tech_admin_cannot_read_state_transfers(api_client) -> None:
    response = api_client.get("/v1/state-transfers", headers=_admin())
    assert response.status_code == 403


def test_state_and_rfb_ingest_remain_blocked(api_client) -> None:
    listing = api_client.get("/v1/data-sources", headers=_analyst())
    by_id = {item["sourceId"]: item for item in listing.json()["items"]}
    assert by_id["ESTADO-ICMS-QUOTA"]["status"] == "DISCOVERED"
    assert by_id["ESTADO-IPVA-QUOTA"]["status"] == "DISCOVERED"
    assert by_id["RFB-DADOS-ABERTOS"]["status"] == "READY_FOR_TERRITORIAL_SCOPE"
    assert by_id["RFB-DADOS-ABERTOS"]["ingestAllowed"] is False
    for source_id in ("ESTADO-ICMS-QUOTA", "ESTADO-IPVA-QUOTA", "RFB-DADOS-ABERTOS"):
        blocked = api_client.post(f"/v1/data-sources/{source_id}/ingest", headers=_admin())
        assert blocked.status_code == 403
