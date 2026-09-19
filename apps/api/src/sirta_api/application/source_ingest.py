import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import (
    DataLoadRow,
    DataLoadRun,
    GoldEnrichment,
    SourceRegistry,
)
from sirta_api.application.audit import record_audit
from sirta_api.application.catalog import _ensure_catalog
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import assert_ingest_allowed
from sirta_api.domain.errors import ForbiddenError, NotVisibleError, ValidationFailedError

FIXTURES = {
    "IBGE-SIDRA": Path("pipelines/synthetic/ibge_sidra_2026_01.json"),
    "TESOURO-TRANSPARENTE": Path("pipelines/synthetic/tesouro_transparente_2026_01.json"),
}
METHODOLOGY_VERSION = "source-enrichment-v1"


def _checksum(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _is_valid(row: dict) -> tuple[bool, str | None]:
    competence = str(row.get("competence") or "")
    value = row.get("value")
    territory = str(row.get("territoryCode") or "")
    if not competence or not territory or value is None or float(value) < 0:
        return False, "invalid competence, territory or value"
    return True, None


def _load_source(session: Session, *, context: AccessContext, source_id: str) -> SourceRegistry:
    _ensure_catalog(session, context=context)
    row = session.scalar(
        select(SourceRegistry).where(
            SourceRegistry.tenant_id == context.tenant_id,
            SourceRegistry.territory_id == context.territory_id,
            SourceRegistry.source_id == source_id,
        )
    )
    if row is None:
        raise NotVisibleError()
    return row


def ingest_catalog_source(session: Session, *, context: AccessContext, source_id: str) -> dict:
    if context.role.value != "tech_admin":
        raise ForbiddenError("Only a technical administrator may run data loads")
    source = _load_source(session, context=context, source_id=source_id)
    assert_ingest_allowed(
        source_role=source.source_role,
        access_classification=source.access_classification,
        status=source.status,
        fixture_kind=source.fixture_kind,
    )
    fixture_path = FIXTURES.get(source_id)
    if fixture_path is None or not fixture_path.exists():
        raise ValidationFailedError("Synthetic fixture is not available for this source")
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    digest = _checksum(payload)
    layout = str(payload.get("layoutVersion") or source.layout_version)
    existing = session.scalar(
        select(DataLoadRun).where(
            DataLoadRun.tenant_id == context.tenant_id,
            DataLoadRun.checksum == digest,
            DataLoadRun.layout_version == layout,
        )
    )
    if existing is not None:
        return _body(existing, source=source, replay=True)
    rows = list(payload.get("rows") or [])
    valid = []
    quarantined = []
    for row in rows:
        ok, reason = _is_valid(row)
        if ok:
            valid.append(row)
        else:
            quarantined.append((row, reason))
    now = datetime.now(UTC)
    run = DataLoadRun(
        id=uuid4(),
        tenant_id=context.tenant_id,
        territory_id=context.territory_id,
        source_id=source_id,
        layout_version=layout,
        competence=str(payload.get("competence") or "2026-01"),
        checksum=digest,
        status="PUBLISHED",
        received_count=len(rows),
        silver_count=len(valid),
        quarantined_count=len(quarantined),
        published=True,
        created_at=now,
    )
    session.add(run)
    session.flush()
    session.add(
        DataLoadRow(
            run_id=run.id,
            row_id="landing-manifest",
            layer="landing",
            status="PRESERVED",
            payload={
                "sourceId": source_id,
                "checksum": digest,
                "officialUrl": source.official_url,
                "competence": run.competence,
            },
        )
    )
    for row in valid:
        session.add(
            DataLoadRow(
                run_id=run.id,
                row_id=str(row["rowId"]),
                layer="silver",
                status="VALIDATED",
                payload={
                    "indicator": row.get("indicator"),
                    "unit": row.get("unit"),
                    "competence": row.get("competence"),
                },
            )
        )
    for row, reason in quarantined:
        session.add(
            DataLoadRow(
                run_id=run.id,
                row_id=str(row.get("rowId") or "unknown"),
                layer="quarantine",
                status="QUARANTINED",
                payload={"indicator": row.get("indicator")},
                reason=reason,
            )
        )
    session.add(
        GoldEnrichment(
            tenant_id=context.tenant_id,
            territory_id=context.territory_id,
            run_id=run.id,
            source_id=source_id,
            source_role=source.source_role,
            published=True,
            indicator_count=len(valid),
            silver_row_count=len(valid),
            methodology_version=METHODOLOGY_VERSION,
            created_at=now,
        )
    )
    record_audit(
        session,
        context=context,
        action="catalog.ingest",
        route=f"/v1/data-sources/{source_id}/ingest",
        outcome="allowed",
        resource_type="data_load_run",
        resource_id=run.id,
    )
    session.flush()
    return _body(run, source=source, replay=False)


def published_enrichment(session: Session, *, context: AccessContext, source_id: str) -> dict:
    context.ensure_fiscal_read()
    gold = session.scalar(
        select(GoldEnrichment)
        .where(
            GoldEnrichment.tenant_id == context.tenant_id,
            GoldEnrichment.territory_id == context.territory_id,
            GoldEnrichment.source_id == source_id,
            GoldEnrichment.published.is_(True),
        )
        .order_by(GoldEnrichment.created_at.desc())
    )
    if gold is None:
        return {
            "sourceId": source_id,
            "published": False,
            "indicatorCount": 0,
            "createsTaxCredit": False,
            "methodologyVersion": METHODOLOGY_VERSION,
            "note": "No published synthetic enrichment Gold.",
        }
    return {
        "sourceId": gold.source_id,
        "sourceRole": gold.source_role,
        "published": True,
        "indicatorCount": gold.indicator_count,
        "createsTaxCredit": False,
        "methodologyVersion": gold.methodology_version,
        "runId": str(gold.run_id),
        "note": "Synthetic enrichment counts. Public sources do not constitute tax credits.",
    }


def _body(run: DataLoadRun, *, source: SourceRegistry, replay: bool) -> dict:
    return {
        "runId": str(run.id),
        "sourceId": source.source_id,
        "status": run.status,
        "checksum": run.checksum,
        "receivedCount": run.received_count,
        "silverCount": run.silver_count,
        "quarantinedCount": run.quarantined_count,
        "landingPreserved": True,
        "published": run.published,
        "replay": replay,
        "taxCreditCreated": False,
        "wouldDownloadFullBase": False,
    }
