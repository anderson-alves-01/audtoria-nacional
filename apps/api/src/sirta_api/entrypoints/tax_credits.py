from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import CollectionCase, TaxCredit, TaxCreditEvidence
from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.audit import record_audit
from sirta_api.application.start_collection import execute_start_collection
from sirta_api.application.validate_credit import execute_validate_credit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.credit import Decision
from sirta_api.domain.errors import NotVisibleError, ValidationFailedError

router = APIRouter()


class CreateTaxCredit(BaseModel):
    tenantId: UUID
    territoryId: UUID
    purposeId: UUID
    taxpayerId: UUID
    taxType: str
    competence: str
    sourceId: str
    principalAmount: Decimal = Field(ge=0)
    additionalAmount: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = "BRL"
    calculationMemory: str = Field(min_length=10)
    enforceabilityStatus: str
    evidenceIds: list[UUID] = Field(min_length=1)


def _to_response(credit: TaxCredit, evidence_ids: list[UUID]) -> dict:
    return {
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
        "evidenceIds": [str(item) for item in evidence_ids],
        "version": credit.version,
    }


class ChecklistItemIn(BaseModel):
    code: str
    satisfied: bool


class ValidationDecision(BaseModel):
    decision: Decision
    checklistVersion: str
    evidenceIds: list[UUID] = Field(min_length=1)
    rationale: str = Field(min_length=10)
    checklistItems: list[ChecklistItemIn] = Field(default_factory=list)


@router.get("/v1/tax-credits")
def list_tax_credits(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
) -> dict:
    context.ensure_fiscal_read()
    rows = session.scalars(
        select(TaxCredit)
        .where(
            TaxCredit.tenant_id == context.tenant_id,
            TaxCredit.territory_id == context.territory_id,
        )
        .order_by(TaxCredit.id)
        .offset(page * size)
        .limit(size)
    ).all()
    record_audit(
        session,
        context=context,
        action="tax_credit.list",
        route="/v1/tax-credits",
        outcome="allowed",
        resource_type="tax_credit",
    )
    items = []
    for credit in rows:
        evidence_ids = [
            row.evidence_id
            for row in session.scalars(
                select(TaxCreditEvidence).where(TaxCreditEvidence.credit_id == credit.id)
            )
        ]
        items.append(_to_response(credit, evidence_ids))
    return {"items": items, "page": page, "size": size}


@router.post("/v1/tax-credits", status_code=201)
def create_tax_credit(
    payload: CreateTaxCredit,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    context.ensure_fiscal_write()
    context.ensure_matching_request(payload.tenantId, payload.territoryId, payload.purposeId)
    if payload.taxType not in {"ISS", "IPTU", "ITBI", "FEE", "IRRF", "OTHER"}:
        raise ValidationFailedError("taxType is not supported")
    credit = TaxCredit(
        id=uuid4(),
        tenant_id=context.tenant_id,
        territory_id=context.territory_id,
        purpose_id=context.purpose_id,
        taxpayer_id=payload.taxpayerId,
        tax_type=payload.taxType,
        competence=payload.competence,
        source_id=payload.sourceId,
        principal_amount=payload.principalAmount,
        additional_amount=payload.additionalAmount,
        currency=payload.currency,
        calculation_memory=payload.calculationMemory,
        enforceability_status=payload.enforceabilityStatus,
        created_by=context.user_id,
    )
    session.add(credit)
    session.flush()
    for evidence_id in payload.evidenceIds:
        session.add(TaxCreditEvidence(credit_id=credit.id, evidence_id=evidence_id))
    record_audit(
        session,
        context=context,
        action="tax_credit.create",
        route="/v1/tax-credits",
        outcome="allowed",
        resource_type="tax_credit",
        resource_id=credit.id,
    )
    return _to_response(credit, payload.evidenceIds)


@router.get("/v1/tax-credits/{credit_id}")
def get_tax_credit(
    credit_id: UUID,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    context.ensure_fiscal_read()
    credit = session.get(TaxCredit, credit_id)
    if credit is None:
        raise NotVisibleError()
    context.ensure_same_tenant(credit.tenant_id)
    context.ensure_same_territory(credit.territory_id)
    evidence_ids = [
        row.evidence_id
        for row in session.scalars(
            select(TaxCreditEvidence).where(TaxCreditEvidence.credit_id == credit.id)
        )
    ]
    record_audit(
        session,
        context=context,
        action="tax_credit.read",
        route="/v1/tax-credits/{creditId}",
        outcome="allowed",
        resource_type="tax_credit",
        resource_id=credit.id,
    )
    return _to_response(credit, evidence_ids)


@router.post("/v1/tax-credits/{credit_id}/validations")
def validate_tax_credit(
    credit_id: UUID,
    payload: ValidationDecision,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    return execute_validate_credit(
        session,
        context=context,
        credit_id=credit_id,
        payload=payload.model_dump(mode="json"),
        idempotency_key=idempotency_key,
    )


@router.post("/v1/tax-credits/{credit_id}/collection-cases", status_code=201)
def start_administrative_collection(
    credit_id: UUID,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict:
    return execute_start_collection(
        session,
        context=context,
        credit_id=credit_id,
        idempotency_key=idempotency_key,
    )


@router.get("/v1/collection-cases")
def list_collection_cases(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
) -> dict:
    context.ensure_fiscal_read()
    rows = session.scalars(
        select(CollectionCase)
        .where(
            CollectionCase.tenant_id == context.tenant_id,
            CollectionCase.territory_id == context.territory_id,
        )
        .order_by(CollectionCase.opened_at)
        .offset(page * size)
        .limit(size)
    ).all()
    record_audit(
        session,
        context=context,
        action="collection_case.list",
        route="/v1/collection-cases",
        outcome="allowed",
        resource_type="collection_case",
    )
    return {
        "items": [
            {
                "id": str(row.id),
                "creditId": str(row.credit_id),
                "status": row.status,
                "slaDueAt": row.sla_due_at.isoformat(),
                "openedAt": row.opened_at.isoformat(),
                "timeline": row.timeline,
            }
            for row in rows
        ],
        "page": page,
        "size": size,
    }
