from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from sirta_api.domain.credit import ValidationStatus
from sirta_api.domain.errors import ConflictError, ForbiddenError
from sirta_api.domain.identities import Role


class CollectionStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    ACTIVE_DEBT = "ACTIVE_DEBT"
    LEGAL_COUNSEL = "LEGAL_COUNSEL"
    JUDICIAL = "JUDICIAL"
    CLOSED = "CLOSED"


class EnforceabilityStatus(StrEnum):
    ENFORCEABLE = "ENFORCEABLE"
    SUSPENDED = "SUSPENDED"
    EXTINGUISHED = "EXTINGUISHED"
    BLOCKED = "BLOCKED"
    LEGAL_REVIEW = "LEGAL_REVIEW"


BLOCKED_ENFORCEABILITY = frozenset(
    {
        EnforceabilityStatus.SUSPENDED,
        EnforceabilityStatus.EXTINGUISHED,
        EnforceabilityStatus.BLOCKED,
        EnforceabilityStatus.LEGAL_REVIEW,
    }
)


@dataclass(frozen=True)
class CollectionCredit:
    credit_id: UUID
    validation_status: ValidationStatus
    enforceability_status: EnforceabilityStatus
    collection_status: CollectionStatus
    version: int


@dataclass(frozen=True)
class CollectionStartResult:
    next_status: CollectionStatus
    next_version: int


def start_administrative_collection(
    *,
    credit: CollectionCredit,
    role: Role,
) -> CollectionStartResult:
    if role != Role.COLLECTOR:
        raise ForbiddenError("Only a collector role may start administrative collection")
    if credit.validation_status is not ValidationStatus.VALIDATED:
        raise ConflictError("No collection without approved validation")
    if credit.enforceability_status in BLOCKED_ENFORCEABILITY:
        raise ConflictError("Suspended, extinguished or blocked credit cannot advance")
    if credit.collection_status is not CollectionStatus.NOT_STARTED:
        raise ConflictError("Collection has already started for this credit")
    return CollectionStartResult(
        next_status=CollectionStatus.ADMINISTRATIVE,
        next_version=credit.version + 1,
    )
