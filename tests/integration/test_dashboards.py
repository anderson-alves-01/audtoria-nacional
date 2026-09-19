from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)
from sirta_api.domain.dashboards import DASHBOARDS


def _analyst() -> dict[str, str]:
    return auth_headers(
        subject=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def test_fifteen_dashboards_are_empty_without_synthetic_fill(api_client) -> None:
    listing = api_client.get("/v1/dashboards", headers=_analyst())
    assert listing.status_code == 200
    body = listing.json()
    assert body["createsTaxCredit"] is False
    assert body["commandsDisabled"] is True
    assert len(body["items"]) == 15
    assert {item["id"] for item in body["items"]} == {item["id"] for item in DASHBOARDS}
    for item in body["items"]:
        assert item["roiCalculated"] is False
        assert item["taxPotentialAsCredit"] is False
        assert item["commandsDisabled"] is True
        assert item["homologationStatus"] == "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
    for catalog in DASHBOARDS:
        detail = api_client.get(f"/v1/dashboards/{catalog['id']}", headers=_analyst())
        assert detail.status_code == 200
        body_detail = detail.json()
        assert body_detail["createsTaxCredit"] is False
        assert body_detail["commandsDisabled"] is True
        assert body_detail["roiCalculated"] is False
        assert body_detail["homologationStatus"] == ("REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION")
        assert body_detail["emptyReason"]
        assert "emptySources" in body_detail
        assert isinstance(body_detail["emptySources"], list)
        if not body_detail["published"]:
            assert body_detail["items"] == []
        else:
            assert all(item["createsTaxCredit"] is False for item in body_detail["items"])
            for item in body_detail["items"]:
                assert "lineage" in item
                assert item.get("homologationStatus") == (
                    "REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION"
                )
    transferencias = api_client.get("/v1/dashboards/transferencias", headers=_analyst()).json()
    assert "Dicionário FPM" in transferencias["emptyReason"]
    if transferencias["published"]:
        assert all(
            item.get("valueKind") != "CATALOG_METADATA" or item.get("financial") is False
            for item in transferencias["items"]
        )
