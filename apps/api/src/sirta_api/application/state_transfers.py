from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.state_transfers import (
    build_state_transfers_panel,
    reject_state_transfers_command,
)


def get_state_transfers(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 30
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_state_transfers_panel(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="state_transfers.read",
        route="/v1/state-transfers",
        outcome="allowed",
        resource_type="state_transfers",
    )
    return snapshot


def state_transfers_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_write()
    record_audit(
        session,
        context=context,
        action="state_transfers.command_rejected",
        route="/v1/state-transfers",
        outcome="denied",
        resource_type="state_transfers",
    )
    reject_state_transfers_command()
