from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.pilot_readiness import build_pilot_readiness_snapshot


def get_pilot_readiness(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_pilot_readiness_snapshot()
    record_audit(
        session,
        context=context,
        action="pilot_readiness.get",
        route="/v1/pilot-readiness",
        outcome="allowed",
        resource_type="pilot_readiness",
        resource_id=None,
    )
    return snapshot
