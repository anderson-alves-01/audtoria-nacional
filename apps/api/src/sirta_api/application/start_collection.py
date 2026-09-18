import hashlib
import json
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import CollectionCase, IdempotencyRecord, TaxCredit
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.collection import (
    CollectionCredit,
    CollectionStatus,
    EnforceabilityStatus,
    start_administrative_collection,
)
from sirta_api.domain.credit import ValidationStatus
from sirta_api.domain.errors import ConflictError, NotVisibleError, ValidationFailedError

SLA_DAYS = 15


def _payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _case_body(case: CollectionCase, credit: TaxCredit) -> dict:
    return {
        "id": str(case.id),
        "creditId": str(credit.id),
        "status": case.status,
        "collectionStatus": credit.collection_status,
        "validationStatus": credit.validation_status,
        "slaDueAt": case.sla_due_at.isoformat(),
        "openedAt": case.opened_at.isoformat(),
        "timeline": case.timeline,
        "version": credit.version,
    }


def execute_start_collection(
    session: Session,
    *,
    context: AccessContext,
    credit_id: UUID,
    idempotency_key: str | None,
) -> dict:
    context.ensure_can_collect()
    if not idempotency_key or len(idempotency_key) < 16:
        raise ValidationFailedError("Idempotency-Key is required")
    credit = session.get(TaxCredit, credit_id)
    if credit is None:
        raise NotVisibleError()
    context.ensure_same_tenant(credit.tenant_id)
    context.ensure_same_territory(credit.territory_id)
    route = "/v1/tax-credits/{creditId}/collection-cases"
    digest = _payload_hash({"creditId": str(credit_id), "command": "StartAdministrativeCollection"})
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
    result = start_administrative_collection(
        credit=CollectionCredit(
            credit_id=credit.id,
            validation_status=ValidationStatus(credit.validation_status),
            enforceability_status=EnforceabilityStatus(credit.enforceability_status),
            collection_status=CollectionStatus(credit.collection_status),
            version=credit.version,
        ),
        role=context.role,
    )
    now = datetime.now(UTC)
    case = CollectionCase(
        id=uuid4(),
        credit_id=credit.id,
        tenant_id=credit.tenant_id,
        territory_id=credit.territory_id,
        actor_id=context.user_id,
        status=result.next_status.value,
        sla_due_at=now + timedelta(days=SLA_DAYS),
        opened_at=now,
        timeline=[
            {
                "at": now.isoformat(),
                "action": "opened",
                "actorId": str(context.user_id),
            }
        ],
    )
    credit.collection_status = result.next_status.value
    credit.version = result.next_version
    session.add(case)
    record_audit(
        session,
        context=context,
        action="tax_credit.collect",
        route=route,
        outcome="allowed",
        resource_type="collection_case",
        resource_id=case.id,
    )
    body = _case_body(case, credit)
    session.add(
        IdempotencyRecord(
            tenant_id=context.tenant_id,
            key=idempotency_key,
            route=route,
            request_hash=digest,
            status_code=201,
            response_body=body,
            created_at=now,
        )
    )
    session.flush()
    return body
