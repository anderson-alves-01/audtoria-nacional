from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import AuditEvent
from sirta_api.domain.authorization import AccessContext


def record_audit(
    session: Session,
    *,
    context: AccessContext,
    action: str,
    route: str,
    outcome: str,
    resource_type: str | None = None,
    resource_id: UUID | None = None,
) -> None:
    session.add(
        AuditEvent(
            occurred_at=datetime.now(UTC),
            tenant_id=context.tenant_id,
            actor_id=context.user_id,
            territory_id=context.territory_id,
            purpose_id=context.purpose_id,
            action=action,
            route=route,
            outcome=outcome,
            resource_type=resource_type,
            resource_id=resource_id,
        )
    )
