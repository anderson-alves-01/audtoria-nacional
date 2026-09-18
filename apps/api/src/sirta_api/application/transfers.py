from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import TaxCredit, TransferOccurrence
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ConflictError, ValidationFailedError

ALLOWED_TYPES = {
    "FPM",
    "ICMS_SHARE",
    "IPVA_SHARE",
    "ITR",
    "IPI_EXPORT",
    "CIDE",
    "FUNDEB",
    "ROYALTY",
    "OTHER",
}


def execute_create_transfer(
    session: Session,
    *,
    context: AccessContext,
    payload: dict,
) -> dict:
    context.ensure_fiscal_read()
    competence = str(payload.get("competence") or "").strip()
    if not competence:
        raise ValidationFailedError("Transfer occurrence requires competence")
    transfer_type = str(payload.get("transferType") or "")
    if transfer_type not in ALLOWED_TYPES:
        raise ValidationFailedError("transferType is not supported")
    source = str(payload.get("officialSource") or "").strip()
    if not source:
        raise ValidationFailedError("officialSource is required")
    existing = session.scalar(
        select(TransferOccurrence).where(
            TransferOccurrence.tenant_id == context.tenant_id,
            TransferOccurrence.transfer_type == transfer_type,
            TransferOccurrence.competence == competence,
            TransferOccurrence.official_source == source,
        )
    )
    if existing is not None:
        raise ConflictError("Duplicate transfer occurrence for source and competence")
    credits_before = session.scalar(
        select(func.count()).select_from(TaxCredit).where(TaxCredit.tenant_id == context.tenant_id)
    )
    occurrence = TransferOccurrence(
        id=uuid4(),
        tenant_id=context.tenant_id,
        territory_id=context.territory_id,
        transfer_type=transfer_type,
        competence=competence,
        official_source=source,
        expected_amount=payload.get("expectedAmount"),
        received_amount=payload.get("receivedAmount") or 0,
        classification="OCCURRENCE_NOT_TAX_CREDIT",
        created_at=datetime.now(UTC),
    )
    session.add(occurrence)
    credits_after = session.scalar(
        select(func.count()).select_from(TaxCredit).where(TaxCredit.tenant_id == context.tenant_id)
    )
    if int(credits_after or 0) != int(credits_before or 0):
        raise ConflictError("Transfer processing must not create a tax credit")
    record_audit(
        session,
        context=context,
        action="transfer.create",
        route="/v1/transfer-occurrences",
        outcome="allowed",
        resource_type="transfer_occurrence",
        resource_id=occurrence.id,
    )
    session.flush()
    return {
        "id": str(occurrence.id),
        "transferType": occurrence.transfer_type,
        "competence": occurrence.competence,
        "classification": occurrence.classification,
        "taxCreditCreated": False,
    }


def list_transfers(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    rows = session.scalars(
        select(TransferOccurrence)
        .where(
            TransferOccurrence.tenant_id == context.tenant_id,
            TransferOccurrence.territory_id == context.territory_id,
        )
        .order_by(TransferOccurrence.competence)
    ).all()
    return {
        "items": [
            {
                "id": str(row.id),
                "transferType": row.transfer_type,
                "competence": row.competence,
                "classification": row.classification,
            }
            for row in rows
        ]
    }
