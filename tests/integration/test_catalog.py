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


def test_catalog_does_not_create_tax_credits_and_blocks_restricted(api_client) -> None:
    listing = api_client.get("/v1/data-sources", headers=_analyst())
    assert listing.status_code == 200
    body = listing.json()
    assert body["officialIngestion"] is True
    assert body["taxCreditCreated"] is False
    by_id = {item["sourceId"]: item for item in body["items"]}
    assert by_id["IBGE-SIDRA"]["createsTaxCredit"] is False
    assert by_id["IBGE-SIDRA"]["ingestAllowed"] is True
    assert by_id["IBGE-SIDRA"]["fixtureKind"] == "OFFICIAL"
    assert by_id["MUNICIPAL-ISS-RESTRICTED"]["ingestAllowed"] is False
    assert by_id["MUNICIPAL-ISS-RESTRICTED"]["status"] == "CREDENTIAL_REQUIRED"
    assert by_id["PORTAL-TRANSPARENCIA-TRANSFERENCIAS"]["ingestAllowed"] is False
    assert by_id["PORTAL-TRANSPARENCIA-TRANSFERENCIAS"]["status"] == "CREDENTIAL_REQUIRED"
    assert by_id["PLANALTO-LC-214"]["ingestAllowed"] is True
    dry = api_client.post("/v1/data-sources/IBGE-SIDRA/dry-run", headers=_analyst())
    assert dry.status_code == 200
    assert dry.json()["wouldCreateTaxCredit"] is False
    assert dry.json()["wouldDownloadFullBase"] is True
    blocked = api_client.post(
        "/v1/data-sources/MUNICIPAL-ISS-RESTRICTED/dry-run", headers=_analyst()
    )
    assert blocked.status_code == 403


def test_tech_admin_cannot_read_source_catalog(api_client) -> None:
    response = api_client.get(
        "/v1/data-sources",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
