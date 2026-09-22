from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.ops_governance import build_ops_governance_snapshot


def get_ops_governance(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_ops_governance_snapshot()
    record_audit(
        session,
        context=context,
        action="ops_governance.get",
        route="/v1/ops-governance",
        outcome="allowed",
        resource_type="ops_governance",
        resource_id=None,
    )
    return snapshot
