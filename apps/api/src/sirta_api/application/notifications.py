from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.notifications import build_notifications_page, reject_notification_send


def list_notifications(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_notifications_page(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="notifications.list",
        route="/v1/notifications",
        outcome="allowed",
        resource_type="administrative_notification",
        resource_id=None,
    )
    return snapshot


def send_notification_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="notifications.send_rejected",
        route="/v1/notifications",
        outcome="denied",
        resource_type="administrative_notification",
        resource_id=None,
    )
    reject_notification_send()
