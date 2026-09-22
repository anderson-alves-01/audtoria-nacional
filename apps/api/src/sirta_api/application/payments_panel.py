from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.payments_panel import build_payments_panel, reject_payment_command


def get_payments_panel(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_payments_panel(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="payments_panel.get",
        route="/v1/payments",
        outcome="allowed",
        resource_type="payments_panel",
        resource_id=None,
    )
    return snapshot


def payment_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="payments_panel.command_rejected",
        route="/v1/payments",
        outcome="denied",
        resource_type="payments_panel",
        resource_id=None,
    )
    reject_payment_command()
