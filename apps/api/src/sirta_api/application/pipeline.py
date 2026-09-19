import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import (
    DataLoadRow,
    DataLoadRun,
    GoldEnrichment,
    GoldFunnel,
    TaxCredit,
)
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ForbiddenError, ValidationFailedError

FIXTURE_PATH = Path("pipelines/synthetic/iss_2026_01.json")
METHODOLOGY_VERSION = "credit-funnel-v1"
LAYOUT_VERSION = "iss-declaration-v1"


def _checksum(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _is_valid(row: dict) -> tuple[bool, str | None]:
    competence = str(row.get("competence") or "")
    amount = row.get("declaredAmount")
    if not competence or amount is None or float(amount) < 0:
        return False, "invalid competence or amount"
    return True, None


def execute_synthetic_iss_load(
    session: Session,
    *,
    context: AccessContext,
    dry_run: bool = False,
) -> dict:
    if context.role.value != "tech_admin":
        raise ForbiddenError("Only a technical administrator may run data loads")
    if not FIXTURE_PATH.exists():
        raise ValidationFailedError("Synthetic ISS fixture is missing")
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    digest = _checksum(payload)
    existing = session.scalar(
        select(DataLoadRun).where(
            DataLoadRun.tenant_id == context.tenant_id,
            DataLoadRun.checksum == digest,
            DataLoadRun.layout_version == LAYOUT_VERSION,
        )
    )
    if existing is not None:
        return _run_body(existing, replay=True)
    rows = list(payload.get("rows") or [])
    valid = []
    quarantined = []
    for row in rows:
        ok, reason = _is_valid(row)
        if ok:
            valid.append(row)
        else:
            quarantined.append((row, reason))
    if dry_run:
        return {
            "status": "DRY_RUN",
            "receivedCount": len(rows),
            "silverCount": len(valid),
            "quarantinedCount": len(quarantined),
            "checksum": digest,
        }
    now = datetime.now(UTC)
    run = DataLoadRun(
        id=uuid4(),
        tenant_id=context.tenant_id,
        territory_id=context.territory_id,
        source_id=str(payload.get("sourceId") or "synthetic-iss-ledger"),
        layout_version=LAYOUT_VERSION,
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
    for row in valid:
        session.add(
            DataLoadRow(
                run_id=run.id,
                row_id=str(row["rowId"]),
                layer="silver",
                status="VALIDATED",
                payload={"activity": row.get("activity"), "competence": row.get("competence")},
            )
        )
    for row, reason in quarantined:
        session.add(
            DataLoadRow(
                run_id=run.id,
                row_id=str(row.get("rowId") or "unknown"),
                layer="quarantine",
                status="QUARANTINED",
                payload={"activity": row.get("activity")},
                reason=reason,
            )
        )
    identified = session.scalar(
        select(func.count())
        .select_from(TaxCredit)
        .where(
            TaxCredit.tenant_id == context.tenant_id,
            TaxCredit.territory_id == context.territory_id,
            TaxCredit.validation_status == "IDENTIFIED",
        )
    )
    validated = session.scalar(
        select(func.count())
        .select_from(TaxCredit)
        .where(
            TaxCredit.tenant_id == context.tenant_id,
            TaxCredit.territory_id == context.territory_id,
            TaxCredit.validation_status == "VALIDATED",
        )
    )
    collecting = session.scalar(
        select(func.count())
        .select_from(TaxCredit)
        .where(
            TaxCredit.tenant_id == context.tenant_id,
            TaxCredit.territory_id == context.territory_id,
            TaxCredit.collection_status == "ADMINISTRATIVE",
        )
    )
    session.add(
        GoldFunnel(
            tenant_id=context.tenant_id,
            territory_id=context.territory_id,
            run_id=run.id,
            published=True,
            identified_count=int(identified or 0),
            validated_count=int(validated or 0),
            in_collection_count=int(collecting or 0),
            silver_row_count=len(valid),
            methodology_version=METHODOLOGY_VERSION,
            created_at=now,
        )
    )
    record_audit(
        session,
        context=context,
        action="data_load.synthetic_iss",
        route="/v1/data-loads/synthetic-iss",
        outcome="allowed",
        resource_type="data_load_run",
        resource_id=run.id,
    )
    session.flush()
    return _run_body(run, replay=False)


def rollback_gold(session: Session, *, context: AccessContext, run_id: UUID) -> dict:
    if context.role.value != "tech_admin":
        raise ForbiddenError("Only a technical administrator may roll back publications")
    run = session.get(DataLoadRun, run_id)
    if run is None or run.tenant_id != context.tenant_id:
        raise ValidationFailedError("Load run is not visible")
    run.published = False
    run.status = "ROLLED_BACK"
    gold = session.scalar(select(GoldFunnel).where(GoldFunnel.run_id == run.id))
    if gold is not None:
        gold.published = False
    enrichment = session.scalar(select(GoldEnrichment).where(GoldEnrichment.run_id == run.id))
    if enrichment is not None:
        enrichment.published = False
    session.flush()
    return _run_body(run, replay=False)


def published_funnel(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    gold = session.scalar(
        select(GoldFunnel)
        .where(
            GoldFunnel.tenant_id == context.tenant_id,
            GoldFunnel.territory_id == context.territory_id,
            GoldFunnel.published.is_(True),
        )
        .order_by(GoldFunnel.created_at.desc())
    )
    if gold is None:
        return {
            "identifiedCount": 0,
            "validatedCount": 0,
            "inCollectionCount": 0,
            "silverRowCount": 0,
            "methodologyVersion": METHODOLOGY_VERSION,
            "published": False,
            "note": "No published synthetic Gold funnel. Regional R$ hypotheses are not KPIs.",
        }
    return {
        "identifiedCount": gold.identified_count,
        "validatedCount": gold.validated_count,
        "inCollectionCount": gold.in_collection_count,
        "silverRowCount": gold.silver_row_count,
        "methodologyVersion": gold.methodology_version,
        "published": True,
        "runId": str(gold.run_id),
        "note": "Synthetic credit counts plus ISS rows. Not economic potential.",
    }


def _run_body(run: DataLoadRun, *, replay: bool) -> dict:
    return {
        "runId": str(run.id),
        "status": run.status,
        "checksum": run.checksum,
        "receivedCount": run.received_count,
        "silverCount": run.silver_count,
        "quarantinedCount": run.quarantined_count,
        "published": run.published,
        "replay": replay,
    }
