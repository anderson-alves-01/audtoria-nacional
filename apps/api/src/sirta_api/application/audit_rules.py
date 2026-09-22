from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.audit_rules import build_audit_rules_catalog
from sirta_api.domain.authorization import AccessContext


def list_audit_rules(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    catalog = build_audit_rules_catalog()
    record_audit(
        session,
        context=context,
        action="audit_rules.list",
        route="/v1/audit-rules",
        outcome="allowed",
        resource_type="audit_rules_catalog",
        resource_id=None,
    )
    return catalog
