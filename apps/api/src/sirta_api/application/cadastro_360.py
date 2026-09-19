from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.cadastro_360 import (
    build_cadastro_360_panel,
    reject_cadastro_360_command,
)


def get_cadastro_360(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_cadastro_360_panel(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="cadastro_360.get",
        route="/v1/cadastro-360",
        outcome="allowed",
        resource_type="cadastro_360",
        resource_id=None,
    )
    return snapshot


def cadastro_360_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="cadastro_360.command_rejected",
        route="/v1/cadastro-360",
        outcome="denied",
        resource_type="cadastro_360",
        resource_id=None,
    )
    reject_cadastro_360_command()
