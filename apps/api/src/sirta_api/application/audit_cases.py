from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.audit_cases import build_audit_cases_page, reject_audit_case_create
from sirta_api.domain.authorization import AccessContext


def list_audit_cases(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_audit_cases_page(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="audit_cases.list",
        route="/v1/cases",
        outcome="allowed",
        resource_type="audit_case",
        resource_id=None,
    )
    return snapshot


def create_audit_case_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="audit_cases.create_rejected",
        route="/v1/cases",
        outcome="denied",
        resource_type="audit_case",
        resource_id=None,
    )
    reject_audit_case_create()
