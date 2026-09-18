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
