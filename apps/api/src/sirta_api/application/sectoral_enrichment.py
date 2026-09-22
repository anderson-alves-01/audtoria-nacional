from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.sectoral_enrichment import (
    build_sectoral_enrichment_panel,
    reject_sectoral_enrichment_command,
)


def get_sectoral_enrichment(
    session: Session, *, context: AccessContext, page: int = 1, size: int = 20
) -> dict:
    context.ensure_fiscal_read()
    snapshot = build_sectoral_enrichment_panel(page=page, size=size)
    record_audit(
        session,
        context=context,
        action="sectoral_enrichment.get",
        route="/v1/sectoral-enrichment",
        outcome="allowed",
        resource_type="sectoral_enrichment",
        resource_id=None,
    )
    return snapshot


def sectoral_enrichment_command_rejected(session: Session, *, context: AccessContext) -> None:
    context.ensure_fiscal_read()
    record_audit(
        session,
        context=context,
        action="sectoral_enrichment.command_rejected",
        route="/v1/sectoral-enrichment",
        outcome="denied",
        resource_type="sectoral_enrichment",
        resource_id=None,
    )
    reject_sectoral_enrichment_command()
