from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.human_validation import build_human_validation_snapshot


def get_human_validation(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_human_validation_snapshot()
    record_audit(
        session,
        context=context,
        action="human_validation.get",
        route="/v1/human-validation",
        outcome="allowed",
        resource_type="human_validation_workflow",
        resource_id=None,
    )
    return snapshot
