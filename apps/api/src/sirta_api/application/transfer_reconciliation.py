from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.transfer_reconciliation import (
    build_transfer_reconciliation_panel,
    reject_reconciliation_command,
)


def get_transfer_reconciliation(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_transfer_reconciliation_panel(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="transfer_reconciliation.get",
        route="/v1/transfer-reconciliation",
        outcome="allowed",
        resource_type="transfer_reconciliation",
        resource_id=None,
    )
    return snapshot


def reconciliation_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="transfer_reconciliation.command_rejected",
        route="/v1/transfer-reconciliation",
        outcome="denied",
        resource_type="transfer_reconciliation",
        resource_id=None,
    )
    reject_reconciliation_command()
