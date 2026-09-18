import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import (
    CreditValidation,
    Evidence,
    IdempotencyRecord,
    TaxCredit,
    TaxCreditEvidence,
)
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.credit import (
    CreditSnapshot,
    Decision,
    EvidenceRef,
    ValidationStatus,
    decide_validation,
)
from sirta_api.domain.errors import ConflictError, NotVisibleError, ValidationFailedError


def _payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def execute_validate_credit(
    session: Session,
    *,
    context: AccessContext,
    credit_id: UUID,
    payload: dict,
    idempotency_key: str | None,
) -> dict:
    context.ensure_can_validate()
    if not idempotency_key or len(idempotency_key) < 16:
        raise ValidationFailedError("Idempotency-Key is required")

    credit = session.get(TaxCredit, credit_id)
    if credit is None:
        raise NotVisibleError()
    context.ensure_same_tenant(credit.tenant_id)
    context.ensure_same_territory(credit.territory_id)

    route = "/v1/tax-credits/{creditId}/validations"
    digest = _payload_hash({"creditId": str(credit_id), **payload})
    existing = session.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.tenant_id == context.tenant_id,
            IdempotencyRecord.key == idempotency_key,
        )
    )
    if existing is not None:
        if existing.request_hash != digest:
            raise ConflictError("Idempotency-Key was reused with a different payload")
        return existing.response_body

    links = session.scalars(
        select(TaxCreditEvidence).where(TaxCreditEvidence.credit_id == credit.id)
    ).all()
    linked_ids = {row.evidence_id for row in links}
    requested = [UUID(str(item)) for item in payload["evidenceIds"]]
    if any(item not in linked_ids for item in requested):
        raise ValidationFailedError("Evidence is not attached to this tax credit")

    evidence_refs: list[EvidenceRef] = []
    for evidence_id in requested:
        row = session.get(Evidence, evidence_id)
        if row is None or row.tenant_id != context.tenant_id:
            raise ValidationFailedError("Evidence hash is missing or invalid")
        evidence_refs.append(EvidenceRef(evidence_id=row.id, sha256=row.sha256))

    result = decide_validation(
        credit=CreditSnapshot(
            credit_id=credit.id,
            created_by=credit.created_by,
            validation_status=ValidationStatus(credit.validation_status),
            version=credit.version,
        ),
        actor_id=context.user_id,
        role=context.role,
        decision=Decision(payload["decision"]),
        checklist_version=str(payload["checklistVersion"]),
        checklist_items=list(payload.get("checklistItems") or []),
        evidence=evidence_refs,
    )

    credit.validation_status = result.next_status.value
    credit.version = result.next_version
    validation = CreditValidation(
        id=uuid4(),
        credit_id=credit.id,
        tenant_id=credit.tenant_id,
        actor_id=context.user_id,
        decision=payload["decision"],
        checklist_version=payload["checklistVersion"],
        checklist_items=list(payload.get("checklistItems") or []),
        rationale=payload["rationale"],
        resulting_status=result.next_status.value,
        created_at=datetime.now(UTC),
    )
    session.add(validation)
    record_audit(
        session,
        context=context,
        action="tax_credit.validate",
        route=route,
        outcome="allowed",
        resource_type="tax_credit",
        resource_id=credit.id,
    )
    body = {
        "id": str(credit.id),
        "tenantId": str(credit.tenant_id),
        "territoryId": str(credit.territory_id),
        "purposeId": str(credit.purpose_id),
        "taxpayerId": str(credit.taxpayer_id),
        "taxType": credit.tax_type,
        "competence": credit.competence,
        "sourceId": credit.source_id,
        "principalAmount": float(credit.principal_amount),
        "additionalAmount": float(credit.additional_amount),
        "currency": credit.currency,
        "calculationMemory": credit.calculation_memory,
        "enforceabilityStatus": credit.enforceability_status,
        "validationStatus": credit.validation_status,
        "collectionStatus": credit.collection_status,
        "paymentStatus": credit.payment_status,
        "evidenceIds": [str(item) for item in requested],
        "version": credit.version,
        "validationId": str(validation.id),
        "decision": payload["decision"],
    }
    session.add(
        IdempotencyRecord(
            tenant_id=context.tenant_id,
            key=idempotency_key,
            route=route,
            request_hash=digest,
            status_code=200,
            response_body=body,
            created_at=datetime.now(UTC),
        )
    )
    session.flush()
    return body
