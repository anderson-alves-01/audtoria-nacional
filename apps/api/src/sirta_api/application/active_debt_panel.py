from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.active_debt_panel import build_active_debt_panel, reject_inscription_command
from sirta_api.domain.authorization import AccessContext


def get_active_debt_panel(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_active_debt_panel()
    record_audit(
        session,
        context=context,
        action="active_debt_panel.get",
        route="/v1/active-debt",
        outcome="allowed",
        resource_type="active_debt_panel",
        resource_id=None,
    )
    return snapshot


def inscription_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="active_debt_panel.inscription_rejected",
        route="/v1/active-debt",
        outcome="denied",
        resource_type="active_debt_panel",
        resource_id=None,
    )
    reject_inscription_command()
