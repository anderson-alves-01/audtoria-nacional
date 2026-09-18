from uuid import uuid4

from sirta_api.domain.collection import (
    CollectionCredit,
    CollectionStatus,
    EnforceabilityStatus,
    start_administrative_collection,
)
from sirta_api.domain.credit import ValidationStatus
from sirta_api.domain.errors import ConflictError, ForbiddenError
from sirta_api.domain.identities import Role

CREDIT_ID = uuid4()


def _credit(
    *,
    validation=ValidationStatus.VALIDATED,
    enforceability=EnforceabilityStatus.ENFORCEABLE,
    collection=CollectionStatus.NOT_STARTED,
    version=2,
) -> CollectionCredit:
    return CollectionCredit(
        credit_id=CREDIT_ID,
        validation_status=validation,
        enforceability_status=enforceability,
        collection_status=collection,
        version=version,
    )


def test_validated_enforceable_credit_starts_administrative_collection() -> None:
    result = start_administrative_collection(credit=_credit(), role=Role.COLLECTOR)
    assert result.next_status == CollectionStatus.ADMINISTRATIVE
    assert result.next_version == 3


def test_identified_credit_cannot_be_collected() -> None:
    try:
        start_administrative_collection(
            credit=_credit(validation=ValidationStatus.IDENTIFIED, version=1),
            role=Role.COLLECTOR,
        )
    except ConflictError as exc:
        assert "validation" in exc.detail.lower()
        return
    raise AssertionError("expected ConflictError")


def test_suspended_credit_cannot_advance() -> None:
    try:
        start_administrative_collection(
            credit=_credit(enforceability=EnforceabilityStatus.SUSPENDED),
            role=Role.COLLECTOR,
        )
    except ConflictError as exc:
        assert "advance" in exc.detail.lower()
        return
    raise AssertionError("expected ConflictError")


def test_validator_cannot_start_collection() -> None:
    try:
        start_administrative_collection(credit=_credit(), role=Role.VALIDATOR)
    except ForbiddenError:
        return
    raise AssertionError("expected ForbiddenError")
