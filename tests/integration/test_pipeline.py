from sqlalchemy import select
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.models import DataLoadRow, DataLoadRun, GoldFunnel
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


def test_synthetic_iss_load_quarantines_invalid_and_is_idempotent(api_client, db_session) -> None:
    first = api_client.post("/v1/data-loads/synthetic-iss", headers=_admin())
    assert first.status_code == 200
    body = first.json()
    assert body["receivedCount"] == 3
    assert body["silverCount"] == 2
    assert body["quarantinedCount"] == 1
    assert body["replay"] is False
    second = api_client.post("/v1/data-loads/synthetic-iss", headers=_admin())
    assert second.status_code == 200
    assert second.json()["runId"] == body["runId"]
    assert second.json()["replay"] is True
    runs = db_session.scalars(select(DataLoadRun)).all()
    assert len(runs) == 1
    rows = db_session.scalars(select(DataLoadRow)).all()
    assert len(rows) == 3
    assert {row.status for row in rows} == {"VALIDATED", "QUARANTINED"}
    gold = db_session.scalars(select(GoldFunnel)).all()
    assert len(gold) == 1
    assert gold[0].identified_count == 1
    assert "declaredAmount" not in str(first.json())


def test_analyst_cannot_run_load_but_can_read_funnel(api_client) -> None:
    denied = api_client.post("/v1/data-loads/synthetic-iss", headers=_analyst())
    assert denied.status_code == 403
    api_client.post("/v1/data-loads/synthetic-iss", headers=_admin())
    funnel = api_client.get("/v1/indicators/credit-funnel", headers=_analyst())
    assert funnel.status_code == 200
    payload = funnel.json()
    assert payload["published"] is True
    assert payload["methodologyVersion"] == "credit-funnel-v1"
    assert payload["identifiedCount"] >= 1


def test_logical_rollback_unpublishes_gold(api_client) -> None:
    loaded = api_client.post("/v1/data-loads/synthetic-iss", headers=_admin())
    run_id = loaded.json()["runId"]
    rolled = api_client.post(f"/v1/data-loads/{run_id}/rollback", headers=_admin())
    assert rolled.status_code == 200
    assert rolled.json()["published"] is False
    funnel = api_client.get("/v1/indicators/credit-funnel", headers=_analyst())
    assert funnel.json()["published"] is False
