from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import RegulatoryItem
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.regulatory import STATUS_NON_BINDING, SYNTHETIC_CATALOG

DISCLAIMER = (
    "Non-binding synthetic catalog. Official dates, rates and layouts require "
    "municipal and legal homologation before operational use."
)


def _ensure_catalog(session: Session, *, context: AccessContext) -> None:
    existing_codes = set(
        session.scalars(
            select(RegulatoryItem.code).where(
                RegulatoryItem.tenant_id == context.tenant_id,
                RegulatoryItem.territory_id == context.territory_id,
            )
        ).all()
    )
    for item in SYNTHETIC_CATALOG:
        if item.code in existing_codes:
            continue
        session.add(
            RegulatoryItem(
                id=uuid4(),
                tenant_id=context.tenant_id,
                territory_id=context.territory_id,
                code=item.code,
                title=item.title,
                source=item.source,
                version=item.version,
                kind=item.kind,
                affected_system=item.affected_system,
                status=STATUS_NON_BINDING,
                binding=False,
                notes=item.notes,
            )
        )
    session.flush()


def list_ibs_cbs_calendar(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    _ensure_catalog(session, context=context)
    rows = session.scalars(
        select(RegulatoryItem)
        .where(
            RegulatoryItem.tenant_id == context.tenant_id,
            RegulatoryItem.territory_id == context.territory_id,
        )
        .order_by(RegulatoryItem.code)
    ).all()
    record_audit(
        session,
        context=context,
        action="regulatory.list",
        route="/v1/regulatory/ibs-cbs",
        outcome="allowed",
        resource_type="regulatory_calendar",
        resource_id=None,
    )
    return {
        "binding": False,
        "operational": False,
        "homologated": False,
        "disclaimer": DISCLAIMER,
        "catalogVersion": "catalog-synthetic-v1",
        "items": [
            {
                "id": str(row.id),
                "code": row.code,
                "title": row.title,
                "source": row.source,
                "version": row.version,
                "kind": row.kind,
                "affectedSystem": row.affected_system,
                "status": row.status,
                "binding": row.binding,
                "notes": row.notes,
            }
            for row in rows
        ],
    }
