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


def test_pilot_readiness_endpoint(api_client) -> None:
    response = api_client.get("/v1/pilot-readiness", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["technicalReady"] is True
    assert body["institutionalReady"] is False
    assert body["pilotMunicipalityApproved"] is False
    assert body["g9Status"] == "BLOCKED"
    assert body["commandsDisabled"] is True
    assert len(body["checklist"]) >= 4


def test_tech_admin_cannot_read_pilot_readiness(api_client) -> None:
    response = api_client.get(
        "/v1/pilot-readiness",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
