from uuid import uuid4

from sirta_api.domain.collection import CollectionStatus
from sirta_api.domain.credit import ValidationStatus
from sirta_api.domain.errors import ConflictError, ForbiddenError, ValidationFailedError
from sirta_api.domain.finance import (
    FinanceCredit,
    PaymentStatus,
    propose_active_debt,
    register_reconciled_payment,
    start_installment,
)
from sirta_api.domain.identities import Role


def test_reconciled_payment_requires_collection() -> None:
    credit = FinanceCredit(
        credit_id=uuid4(),
        validation_status=ValidationStatus.VALIDATED,
        collection_status=CollectionStatus.NOT_STARTED,
        payment_status=PaymentStatus.OPEN,
        version=2,
    )
    try:
        register_reconciled_payment(
            credit=credit, role=Role.COLLECTOR, reconciliation_ref="bank-001"
        )
    except ConflictError:
        return
    raise AssertionError("expected ConflictError")


def test_payment_without_reconciliation_is_rejected() -> None:
    credit = FinanceCredit(
        credit_id=uuid4(),
        validation_status=ValidationStatus.VALIDATED,
        collection_status=CollectionStatus.ADMINISTRATIVE,
        payment_status=PaymentStatus.OPEN,
        version=3,
    )
    try:
        register_reconciled_payment(credit=credit, role=Role.COLLECTOR, reconciliation_ref=" ")
    except ValidationFailedError:
        return
    raise AssertionError("expected ValidationFailedError")


def test_debt_officer_cannot_be_analyst() -> None:
    credit = FinanceCredit(
        credit_id=uuid4(),
        validation_status=ValidationStatus.VALIDATED,
        collection_status=CollectionStatus.ADMINISTRATIVE,
        payment_status=PaymentStatus.OPEN,
        version=3,
    )
    try:
        propose_active_debt(credit=credit, role=Role.ANALYST)
    except ForbiddenError:
        return
    raise AssertionError("expected ForbiddenError")


def test_installment_from_collected_validated_credit() -> None:
    credit = FinanceCredit(
        credit_id=uuid4(),
        validation_status=ValidationStatus.VALIDATED,
        collection_status=CollectionStatus.ADMINISTRATIVE,
        payment_status=PaymentStatus.OPEN,
        version=3,
    )
    status, version = start_installment(credit=credit, role=Role.COLLECTOR)
    assert status == PaymentStatus.INSTALLMENT_CURRENT
    assert version == 4
