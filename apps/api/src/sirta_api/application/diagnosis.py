from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.diagnosis import build_diagnosis_snapshot


def get_diagnosis(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_diagnosis_snapshot()
    record_audit(
        session,
        context=context,
        action="diagnosis.get",
        route="/v1/diagnosis",
        outcome="allowed",
        resource_type="municipal_diagnosis",
        resource_id=None,
    )
    return snapshot
