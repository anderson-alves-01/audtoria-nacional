from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import TaxCredit
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.collection import CollectionStatus
from sirta_api.domain.credit import ValidationStatus
from sirta_api.domain.errors import NotVisibleError
from sirta_api.domain.finance import (
    FinanceCredit,
    PaymentStatus,
    propose_active_debt,
    register_reconciled_payment,
    start_installment,
)


def _load(session: Session, context: AccessContext, credit_id: UUID) -> TaxCredit:
    credit = session.get(TaxCredit, credit_id)
    if credit is None:
        raise NotVisibleError()
    context.ensure_same_tenant(credit.tenant_id)
    context.ensure_same_territory(credit.territory_id)
    return credit


def _snapshot(credit: TaxCredit) -> FinanceCredit:
    return FinanceCredit(
        credit_id=credit.id,
        validation_status=ValidationStatus(credit.validation_status),
        collection_status=CollectionStatus(credit.collection_status),
        payment_status=PaymentStatus(credit.payment_status),
        version=credit.version,
    )


def _body(credit: TaxCredit) -> dict:
    return {
        "creditId": str(credit.id),
        "validationStatus": credit.validation_status,
        "collectionStatus": credit.collection_status,
        "paymentStatus": credit.payment_status,
        "version": credit.version,
    }


def execute_payment(
    session: Session,
    *,
    context: AccessContext,
    credit_id: UUID,
    reconciliation_ref: str,
) -> dict:
    context.ensure_can_collect()
    credit = _load(session, context, credit_id)
    status, version = register_reconciled_payment(
        credit=_snapshot(credit),
        role=context.role,
        reconciliation_ref=reconciliation_ref,
    )
    credit.payment_status = status.value
    credit.version = version
    record_audit(
        session,
        context=context,
        action="tax_credit.payment",
        route="/v1/tax-credits/{creditId}/payments",
        outcome="allowed",
        resource_type="tax_credit",
        resource_id=credit.id,
    )
    session.flush()
    return _body(credit)


def execute_installment(session: Session, *, context: AccessContext, credit_id: UUID) -> dict:
    context.ensure_can_collect()
    credit = _load(session, context, credit_id)
    status, version = start_installment(credit=_snapshot(credit), role=context.role)
    credit.payment_status = status.value
    credit.version = version
    record_audit(
        session,
        context=context,
        action="tax_credit.installment",
        route="/v1/tax-credits/{creditId}/installments",
        outcome="allowed",
        resource_type="tax_credit",
        resource_id=credit.id,
    )
    session.flush()
    return _body(credit)


def execute_active_debt(session: Session, *, context: AccessContext, credit_id: UUID) -> dict:
    context.ensure_can_propose_debt()
    credit = _load(session, context, credit_id)
    status, version = propose_active_debt(credit=_snapshot(credit), role=context.role)
    credit.collection_status = status.value
    credit.version = version
    record_audit(
        session,
        context=context,
        action="tax_credit.active_debt",
        route="/v1/tax-credits/{creditId}/active-debt-proposals",
        outcome="allowed",
        resource_type="tax_credit",
        resource_id=credit.id,
    )
    session.flush()
    return _body(credit)


def now_utc() -> datetime:
    return datetime.now(UTC)
