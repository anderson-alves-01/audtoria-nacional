from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.procuradoria_panel import build_procuradoria_panel, reject_legal_command


def get_procuradoria_panel(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_procuradoria_panel()
    record_audit(
        session,
        context=context,
        action="procuradoria_panel.get",
        route="/v1/procuradoria",
        outcome="allowed",
        resource_type="procuradoria_panel",
        resource_id=None,
    )
    return snapshot


def legal_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="procuradoria_panel.command_rejected",
        route="/v1/procuradoria",
        outcome="denied",
        resource_type="procuradoria_panel",
        resource_id=None,
    )
    reject_legal_command()
