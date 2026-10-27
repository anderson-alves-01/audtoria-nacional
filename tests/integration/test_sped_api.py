import hashlib
from pathlib import Path

from sqlalchemy import func, select
from tests.helpers.sped_fixture import build_sped_workbook
from tests.helpers.tokens import auth_headers

from sirta_api.adapters.db.models import AuditEvent, DataLoadRun, SpedOperationFact
from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    PURPOSE_BETA_ACTIVE,
    TENANT_ALPHA,
    TENANT_BETA,
    TERRITORY_ALPHA_CENTRO,
    TERRITORY_BETA_SEDE,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
    USER_ANALYST_BETA,
)
from sirta_api.config import get_settings

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
UPLOAD = "/v1/data-sources/SPED-NFE-UF-CFOP/upload"


def _alpha(subject) -> dict[str, str]:
    return auth_headers(
        subject=subject,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
    )


def _admin() -> dict[str, str]:
    return _alpha(USER_ADMIN_ALPHA)


def _analyst() -> dict[str, str]:
    return _alpha(USER_ANALYST_ALPHA)


def _upload(api_client, body: bytes, headers: dict[str, str] | None = None):
    return api_client.post(
        UPLOAD,
        content=body,
        headers={**(headers or _admin()), "Content-Type": XLSX},
    )


def _facts(db_session) -> int:
    return int(db_session.scalar(select(func.count()).select_from(SpedOperationFact)) or 0)


def test_upload_loads_bronze_silver_gold_once_and_replays(api_client, db_session) -> None:
    workbook = build_sped_workbook()
    first = _upload(api_client, workbook)
    assert first.status_code == 200, first.text
    body = first.json()
    assert body["status"] == "VALIDATED"
    assert body["replay"] is False
    assert body["published"] is False
    assert body["homologated"] is False
    assert body["createsTaxCredit"] is False
    assert body["valueKind"] == "ESTIMATED_ALLOCATION"
    assert body["checksum"] == hashlib.sha256(workbook).hexdigest()
    assert body["competence"] == "2021-25"
    assert body["reconciliation"]["ok"] is True
    loaded = _facts(db_session)
    assert loaded == body["silverCount"] == body["receivedCount"] > 945

    second = _upload(api_client, workbook)
    assert second.status_code == 200
    assert second.json()["replay"] is True
    assert second.json()["runId"] == body["runId"]
    assert _facts(db_session) == loaded

    actions = set(db_session.scalars(select(AuditEvent.action)).all())
    assert {"sped.upload", "sped.upload.replay"} <= actions


def test_landing_keeps_the_original_file_with_its_checksum(api_client) -> None:
    workbook = build_sped_workbook()
    assert _upload(api_client, workbook).status_code == 200
    digest = hashlib.sha256(workbook).hexdigest()
    payloads = list(
        Path(get_settings().datalake_root).glob(f"landing/SPED-NFE-UF-CFOP/*/*/{digest}")
    )
    assert payloads, "landing directory with the checksum is missing"
    assert (payloads[0] / "payload.bin").read_bytes() == workbook
    assert (payloads[0] / "manifest.json").exists()


def test_only_the_technical_administrator_uploads(api_client, db_session) -> None:
    response = _upload(api_client, build_sped_workbook(), headers=_analyst())
    assert response.status_code == 403
    assert _facts(db_session) == 0


def test_unknown_source_and_generic_ingest_are_refused(api_client) -> None:
    other = api_client.post(
        "/v1/data-sources/IBGE-SIDRA/upload",
        content=build_sped_workbook(),
        headers={**_admin(), "Content-Type": "application/octet-stream"},
    )
    assert other.status_code == 404
    generic = api_client.post("/v1/data-sources/SPED-NFE-UF-CFOP/ingest", headers=_admin())
    assert generic.status_code == 403


def test_inconsistent_workbook_is_quarantined_and_never_read(api_client, db_session) -> None:
    broken = build_sped_workbook(mutate_base=lambda rows: rows[0].__setitem__(3, 999999))
    response = _upload(api_client, broken)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "QUARANTINED"
    assert body["silverCount"] == 0
    assert body["quarantinedCount"] == body["receivedCount"]
    assert body["reconciliation"]["ok"] is False
    assert _facts(db_session) == 0
    run = db_session.scalar(select(DataLoadRun).where(DataLoadRun.id == body["runId"]))
    assert run is not None and run.published is False
    read = api_client.get("/v1/sped-operacoes", headers=_analyst())
    assert read.status_code == 200
    assert read.json()["run"] is None
    assert read.json()["items"] == []


def test_invalid_layout_is_a_validation_error(api_client, db_session) -> None:
    response = _upload(api_client, build_sped_workbook(drop_sheet="Base CFOP"))
    assert response.status_code == 422
    assert "Base CFOP" in response.json()["detail"]
    assert _upload(api_client, b"not an xlsx").status_code == 422
    assert _upload(api_client, b"").status_code == 422
    assert _facts(db_session) == 0


def test_read_returns_series_with_filters_pagination_and_null_values(api_client) -> None:
    assert _upload(api_client, build_sped_workbook()).status_code == 200
    series = api_client.get("/v1/sped-operacoes?pageSize=1000", headers=_analyst()).json()
    assert series["total"] == 945
    assert series["valueKind"] == "ESTIMATED_ALLOCATION"
    assert series["homologated"] is False
    assert series["createsTaxCredit"] is False
    assert series["run"]["checksum"]
    assert "rateio" in series["banner"].lower()
    assert any(
        item["valorEstimado"] is None and item["quantidade"] == 0 for item in series["items"]
    )
    assert all(
        item["valorEstimado"] is None or isinstance(item["valorEstimado"], str)
        for item in series["items"]
    )

    filtered = api_client.get(
        "/v1/sped-operacoes?ano=2023&uf=SP&operacao=Vendas", headers=_analyst()
    ).json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["ano"] == 2023 and filtered["items"][0]["uf"] == "SP"

    page = api_client.get(
        "/v1/sped-operacoes?level=CFOP&uf=SP&pageSize=5&page=2", headers=_analyst()
    ).json()
    assert len(page["items"]) == 5 and page["page"] == 2 and page["total"] > 5
    assert all("cfop" in item for item in page["items"])
    by_cfop = api_client.get("/v1/sped-operacoes?level=CFOP&cfop=5102", headers=_analyst()).json()
    assert by_cfop["total"] > 0 and all(item["cfop"] == "5102" for item in by_cfop["items"])


def test_read_rejects_invalid_filters(api_client) -> None:
    for query in ("ano=2019", "uf=XX", "operacao=Qualquer", "cfop=12", "level=OUTRO"):
        response = api_client.get(f"/v1/sped-operacoes?{query}", headers=_analyst())
        assert response.status_code == 422, query


def test_technical_administrator_session_without_operator_login_cannot_read(api_client) -> None:
    assert api_client.get("/v1/sped-operacoes", headers=_admin()).status_code == 403


def test_other_tenant_never_sees_the_load(api_client, db_session) -> None:
    assert _upload(api_client, build_sped_workbook()).status_code == 200
    beta = auth_headers(
        subject=USER_ANALYST_BETA,
        tenant_id=TENANT_BETA,
        territory_id=TERRITORY_BETA_SEDE,
        purpose_id=PURPOSE_BETA_ACTIVE,
    )
    response = api_client.get("/v1/sped-operacoes?pageSize=1000", headers=beta)
    assert response.status_code == 200
    assert response.json()["run"] is None
    assert response.json()["items"] == []
    assert response.json()["total"] == 0
    assert api_client.get("/v1/sped-operacoes", headers={}).status_code == 401
    alpha_facts = db_session.scalar(
        select(func.count())
        .select_from(SpedOperationFact)
        .where(SpedOperationFact.tenant_id == TENANT_ALPHA)
    )
    beta_facts = db_session.scalar(
        select(func.count())
        .select_from(SpedOperationFact)
        .where(SpedOperationFact.tenant_id == TENANT_BETA)
    )
    assert alpha_facts and beta_facts == 0
