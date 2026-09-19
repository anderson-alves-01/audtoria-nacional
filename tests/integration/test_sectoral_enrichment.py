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


def test_sectoral_enrichment_endpoint_is_empty_shell(api_client) -> None:
    response = api_client.get("/v1/sectoral-enrichment", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["ingestEnabled"] is False
    assert body["createsTaxCredit"] is False
    assert body["commandsDisabled"] is True
    assert body["items"] == []
    assert body["total"] == 0
    assert body["institutionalStatus"] == "DISCOVERED"
    assert len(body["sources"]) == 6
    source_ids = {row["sourceId"] for row in body["sources"]}
    assert source_ids == {
        "ANP-REVENDEDORES",
        "ANEEL-DADOS-ABERTOS",
        "EPE-DADOS-ABERTOS",
        "ANATEL-DADOS-ABERTOS",
        "BCB-SGS-OLINDA",
        "CNES-DATASUS",
    }


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


def test_sectoral_sources_listed_and_ingest_blocked(api_client) -> None:
    listing = api_client.get("/v1/data-sources", headers=_analyst())
    by_id = {item["sourceId"]: item for item in listing.json()["items"]}
    for source_id in (
        "ANP-REVENDEDORES",
        "ANEEL-DADOS-ABERTOS",
        "EPE-DADOS-ABERTOS",
        "ANATEL-DADOS-ABERTOS",
        "BCB-SGS-OLINDA",
        "CNES-DATASUS",
    ):
        assert by_id[source_id]["status"] == "DISCOVERED"
        assert by_id[source_id]["ingestAllowed"] is False
        assert by_id[source_id]["createsTaxCredit"] is False
    blocked = api_client.post("/v1/data-sources/ANP-REVENDEDORES/ingest", headers=_admin())
    assert blocked.status_code == 403


def _admin() -> dict[str, str]:
    return auth_headers(
        subject=USER_ADMIN_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
