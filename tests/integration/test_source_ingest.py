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


def test_catalog_ingest_ibge_is_idempotent_and_never_creates_tax_credit(api_client) -> None:
    first = api_client.post("/v1/data-sources/IBGE-SIDRA/ingest", headers=_admin())
    assert first.status_code == 200
    body = first.json()
    assert body["sourceId"] == "IBGE-SIDRA"
    assert body["receivedCount"] == 3
    assert body["silverCount"] == 2
    assert body["quarantinedCount"] == 1
    assert body["landingPreserved"] is True
    assert body["taxCreditCreated"] is False
    assert body["wouldDownloadFullBase"] is True
    assert body["homologationStatus"] == "REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY"
    second = api_client.post("/v1/data-sources/IBGE-SIDRA/ingest", headers=_admin())
    assert second.status_code == 200
    assert second.json()["runId"] == body["runId"]
    assert second.json()["replay"] is True


def test_restricted_source_ingest_is_forbidden(api_client) -> None:
    response = api_client.post("/v1/data-sources/MUNICIPAL-ISS-RESTRICTED/ingest", headers=_admin())
    assert response.status_code == 403


def test_analyst_cannot_ingest_but_can_read_enrichment(api_client) -> None:
    denied = api_client.post("/v1/data-sources/IBGE-SIDRA/ingest", headers=_analyst())
    assert denied.status_code == 403
    api_client.post("/v1/data-sources/IBGE-SIDRA/ingest", headers=_admin())
    gold = api_client.get(
        "/v1/indicators/source-enrichment",
        headers=_analyst(),
        params={"sourceId": "IBGE-SIDRA"},
    )
    assert gold.status_code == 200
    payload = gold.json()
    assert payload["published"] is True
    assert payload["createsTaxCredit"] is False
    assert payload["indicatorCount"] == 2
    assert payload["sourceRole"] == "REFERENCE_ENRICHMENT"
    assert payload["homologationStatus"] == "REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY"
    assert "NÃO É CRÉDITO TRIBUTÁRIO" in payload["banner"]


def test_logical_rollback_unpublishes_enrichment(api_client) -> None:
    loaded = api_client.post("/v1/data-sources/IBGE-SIDRA/ingest", headers=_admin())
    run_id = loaded.json()["runId"]
    rolled = api_client.post(f"/v1/data-loads/{run_id}/rollback", headers=_admin())
    assert rolled.status_code == 200
    gold = api_client.get(
        "/v1/indicators/source-enrichment",
        headers=_analyst(),
        params={"sourceId": "IBGE-SIDRA"},
    )
    assert gold.status_code == 200
    payload = gold.json()
    assert payload["createsTaxCredit"] is False
    if payload.get("runId") == run_id:
        assert payload["published"] is False


def test_catalog_ingest_tesouro_stub_never_creates_tax_credit(api_client) -> None:
    first = api_client.post("/v1/data-sources/TESOURO-TRANSPARENTE/ingest", headers=_admin())
    assert first.status_code == 200
    body = first.json()
    assert body["sourceId"] == "TESOURO-TRANSPARENTE"
    assert body["receivedCount"] == 18
    assert body["silverCount"] == 18
    assert body["quarantinedCount"] == 0
    assert body["taxCreditCreated"] is False
    assert body["wouldDownloadFullBase"] is True
    second = api_client.post("/v1/data-sources/TESOURO-TRANSPARENTE/ingest", headers=_admin())
    assert second.json()["runId"] == body["runId"]
    gold = api_client.get(
        "/v1/indicators/source-enrichment",
        headers=_analyst(),
        params={"sourceId": "TESOURO-TRANSPARENTE"},
    )
    assert gold.status_code == 200
    payload = gold.json()
    assert payload["published"] is True
    assert payload["createsTaxCredit"] is False
    assert payload["sourceRole"] == "OFFICIAL_TRANSFER"
    assert payload["indicatorCount"] == 18
