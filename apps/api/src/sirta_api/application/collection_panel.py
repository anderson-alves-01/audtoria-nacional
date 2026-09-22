from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.collection_panel import build_collection_panel


def get_collection_panel(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_collection_panel()
    record_audit(
        session,
        context=context,
        action="collection_panel.get",
        route="/v1/collection",
        outcome="allowed",
        resource_type="collection_panel",
        resource_id=None,
    )
    return snapshot
