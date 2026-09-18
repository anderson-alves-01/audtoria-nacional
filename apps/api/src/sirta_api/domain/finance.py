from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from sirta_api.domain.collection import CollectionStatus
from sirta_api.domain.credit import ValidationStatus
from sirta_api.domain.errors import ConflictError, ForbiddenError, ValidationFailedError
from sirta_api.domain.identities import Role


class PaymentStatus(StrEnum):
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    COMPENSATED = "COMPENSATED"
    INSTALLMENT_CURRENT = "INSTALLMENT_CURRENT"
    INSTALLMENT_BREACHED = "INSTALLMENT_BREACHED"


@dataclass(frozen=True)
class FinanceCredit:
    credit_id: UUID
    validation_status: ValidationStatus
    collection_status: CollectionStatus
    payment_status: PaymentStatus
    version: int


def register_reconciled_payment(*, credit: FinanceCredit, role: Role, reconciliation_ref: str):
    if role != Role.COLLECTOR:
        raise ForbiddenError("Only a collector may register a reconciled payment")
    if not reconciliation_ref.strip():
        raise ValidationFailedError("Recovered value requires a payment reconciliation reference")
    if credit.collection_status is CollectionStatus.NOT_STARTED:
        raise ConflictError("Payment cannot be recovered before administrative collection")
    if credit.validation_status is not ValidationStatus.VALIDATED:
        raise ConflictError("Payment cannot be recovered on an unvalidated credit")
    return PaymentStatus.PAID, credit.version + 1


def start_installment(*, credit: FinanceCredit, role: Role):
    if role != Role.COLLECTOR:
        raise ForbiddenError("Only a collector may start an installment agreement")
    if credit.validation_status is not ValidationStatus.VALIDATED:
        raise ConflictError("Installment requires an approved validation")
    if credit.collection_status is CollectionStatus.NOT_STARTED:
        raise ConflictError("Installment requires an open administrative collection")
    return PaymentStatus.INSTALLMENT_CURRENT, credit.version + 1


def propose_active_debt(*, credit: FinanceCredit, role: Role):
    if role != Role.DEBT_OFFICER:
        raise ForbiddenError("Only a debt officer may propose active-debt inscription")
    if credit.validation_status is not ValidationStatus.VALIDATED:
        raise ConflictError("Active debt requires an approved validation")
    if credit.collection_status is CollectionStatus.NOT_STARTED:
        raise ConflictError("Active debt requires prior administrative collection")
    return CollectionStatus.ACTIVE_DEBT, credit.version + 1
