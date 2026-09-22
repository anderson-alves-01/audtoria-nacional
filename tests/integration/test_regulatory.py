from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
)
from sirta_api.domain.regulatory import SYNTHETIC_CATALOG


def _analyst() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_ibs_cbs_calendar_is_non_binding_and_idempotent(api_client) -> None:
    first = api_client.get("/v1/regulatory/ibs-cbs", headers=_analyst())
    second = api_client.get("/v1/regulatory/ibs-cbs", headers=_analyst())
    assert first.status_code == 200
    assert second.status_code == 200
    body = first.json()
    assert body["binding"] is False
    assert body["operational"] is False
    assert body["homologated"] is False
    assert "non-binding" in body["disclaimer"].lower()
    assert body["catalogVersion"] == "catalog-official-docs-v1"
    assert "preservedDocuments" in body
    assert isinstance(body["preservedDocuments"], list)
    assert len(body["items"]) == len(SYNTHETIC_CATALOG)
    assert len(second.json()["items"]) == len(body["items"])
    assert all(item["binding"] is False for item in body["items"])
    assert all(item["status"] == "NON_BINDING" for item in body["items"])
    assert all(item.get("homologated") is not True for item in body["items"])


def test_tech_admin_cannot_read_regulatory_calendar(api_client) -> None:
    response = api_client.get(
        "/v1/regulatory/ibs-cbs",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403


def test_calendar_links_preserved_documents_after_planalto_ingest(api_client) -> None:
    admin = auth_headers(
        subject=USER_ADMIN_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )
    for source_id in ("PLANALTO-LEGISLACAO", "PLANALTO-LC-214"):
        ingested = api_client.post(f"/v1/data-sources/{source_id}/ingest", headers=admin)
        assert ingested.status_code == 200
        assert ingested.json()["taxCreditCreated"] is False

    calendar = api_client.get("/v1/regulatory/ibs-cbs", headers=_analyst())
    assert calendar.status_code == 200
    body = calendar.json()
    assert body["binding"] is False
    assert body["operational"] is False
    assert body["homologated"] is False
    assert body["catalogVersion"] == "catalog-official-docs-v1"
    by_source = {doc["sourceId"]: doc for doc in body["preservedDocuments"]}
    for source_id in ("PLANALTO-LEGISLACAO", "PLANALTO-LC-214"):
        doc = by_source[source_id]
        assert doc["published"] is True
        assert doc["bronzeSha256"]
        assert doc["checksumSha256"]
        assert doc["landingManifestPath"]
        assert doc["officialUrl"]
        assert doc["binding"] is False
        assert doc["operational"] is False
        assert doc["homologated"] is False
    assert any(item["code"] == "LC-214-2025" for item in body["items"])
