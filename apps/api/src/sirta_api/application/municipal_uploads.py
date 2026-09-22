from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.municipal_uploads import (
    build_municipal_uploads_panel,
    reject_municipal_upload_command,
)


def get_municipal_uploads(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_municipal_uploads_panel(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="municipal_uploads.get",
        route="/v1/municipal-uploads",
        outcome="allowed",
        resource_type="municipal_uploads",
        resource_id=None,
    )
    return snapshot


def municipal_upload_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="municipal_uploads.command_rejected",
        route="/v1/municipal-uploads",
        outcome="denied",
        resource_type="municipal_uploads",
        resource_id=None,
    )
    reject_municipal_upload_command()
