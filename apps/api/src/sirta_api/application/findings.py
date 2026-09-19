from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.findings import build_findings_page


def list_findings(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_findings_page(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="findings.list",
        route="/v1/findings",
        outcome="allowed",
        resource_type="audit_finding",
        resource_id=None,
    )
    return snapshot
