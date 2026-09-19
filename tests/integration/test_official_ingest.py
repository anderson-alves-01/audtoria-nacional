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
    assert body["published"] is False
    assert body["createsTaxCredit"] is False
    assert "HOMOLOGAÇÃO HUMANA PENDENTE" in body["banner"]
    assert any(item["sourceId"] == "ESTADO-ICMS-QUOTA" for item in body["emptySources"])


def test_siconfi_entes_and_ibge_pib_and_planalto_ingest(api_client) -> None:
    siconfi = api_client.post("/v1/data-sources/SICONFI-ENTES/ingest", headers=_admin())
    assert siconfi.status_code == 200
    assert siconfi.json()["silverCount"] == 2
    assert siconfi.json()["quarantinedCount"] == 1
    pib = api_client.post("/v1/data-sources/IBGE-SIDRA-PIB/ingest", headers=_admin())
    assert pib.status_code == 200
    assert pib.json()["silverCount"] == 2
    assert pib.json()["quarantinedCount"] == 2
    planalto = api_client.post("/v1/data-sources/PLANALTO-LEGISLACAO/ingest", headers=_admin())
    assert planalto.status_code == 200
    assert planalto.json()["silverCount"] == 1
    blocked = api_client.post("/v1/data-sources/TESOURO-FPM-VALORES/ingest", headers=_admin())
    assert blocked.status_code == 403
    gold = api_client.get("/v1/indicators/official-gold", headers=_analyst())
    body = gold.json()
    assert body["published"] is True
    ids = {item["sourceId"] for item in body["items"]}
    assert {"SICONFI-ENTES", "IBGE-SIDRA-PIB", "PLANALTO-LEGISLACAO"} <= ids
    assert all(
        item["homologationStatus"] == "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
        for item in body["items"]
    )
    assert all(item["createsTaxCredit"] is False for item in body["items"])


def test_unavailable_sources_stay_empty(api_client) -> None:
    listing = api_client.get("/v1/data-sources", headers=_analyst())
    by_id = {item["sourceId"]: item for item in listing.json()["items"]}
    assert by_id["TESOURO-FPM-VALORES"]["status"] == "UNAVAILABLE"
    assert by_id["ESTADO-ICMS-QUOTA"]["status"] == "DISCOVERED"
    assert by_id["RFB-DADOS-ABERTOS"]["ingestAllowed"] is False
