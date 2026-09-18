from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import AuditEvent
from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/audit-events")
def list_audit_events(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
) -> dict:
    rows = session.scalars(
        select(AuditEvent)
        .where(AuditEvent.tenant_id == context.tenant_id)
        .order_by(AuditEvent.occurred_at.desc())
        .offset(page * size)
        .limit(size)
    ).all()
    return {
        "items": [
            {
                "id": str(item.id),
                "occurredAt": item.occurred_at.isoformat(),
                "tenantId": str(item.tenant_id),
                "actorId": str(item.actor_id),
                "action": item.action,
                "route": item.route,
                "outcome": item.outcome,
                "resourceType": item.resource_type,
                "resourceId": str(item.resource_id) if item.resource_id else None,
            }
            for item in rows
        ],
        "page": page,
        "size": size,
    }
