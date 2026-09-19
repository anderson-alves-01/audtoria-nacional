from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.gates import program_snapshot


def list_program_gates(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = program_snapshot()
    record_audit(
        session,
        context=context,
        action="gates.list",
        route="/v1/program-gates",
        outcome="allowed",
        resource_type="program_gate",
    )
    return snapshot
