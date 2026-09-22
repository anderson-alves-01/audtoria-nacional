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


def test_diagnosis_endpoint_is_empty_technical_shell(api_client) -> None:
    response = api_client.get("/v1/diagnosis", headers=_analyst())
    assert response.status_code == 200
    body = response.json()
    assert body["binding"] is False
    assert body["operational"] is False
    assert body["homologated"] is False
    assert body["commandsDisabled"] is True
    assert body["recoveryMeta"] is None
    assert body["items"] == []
    assert body["checklist"]
    assert all(item["met"] is False for item in body["checklist"])
    assert "g1Status" in body
    assert body["g1Status"] == "BLOCKED"


def test_tech_admin_cannot_read_diagnosis(api_client) -> None:
    response = api_client.get(
        "/v1/diagnosis",
        headers=auth_headers(
            subject=USER_ADMIN_ALPHA,
            tenant_id=TENANT_ALPHA,
            territory_id=TERRITORY_ALPHA_CENTRO,
            purpose_id=PURPOSE_ALPHA_ACTIVE,
        ),
    )
    assert response.status_code == 403
