from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from sirta_api.domain.checklist import CHECKLIST_VERSION as CURRENT_CHECKLIST
from sirta_api.domain.checklist import required_item_codes
from sirta_api.domain.errors import ConflictError, ForbiddenError, ValidationFailedError
from sirta_api.domain.identities import Role

CHECKLIST_VERSION = CURRENT_CHECKLIST
SHA256_LENGTH = 64


class ValidationStatus(StrEnum):
    IDENTIFIED = "IDENTIFIED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Decision(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_INFORMATION = "REQUEST_INFORMATION"


OPEN_STATUSES = frozenset({ValidationStatus.IDENTIFIED, ValidationStatus.UNDER_REVIEW})

DECISION_TO_STATUS = {
    Decision.APPROVE: ValidationStatus.VALIDATED,
    Decision.REJECT: ValidationStatus.REJECTED,
    Decision.REQUEST_INFORMATION: ValidationStatus.UNDER_REVIEW,
}


@dataclass(frozen=True)
class CreditSnapshot:
    credit_id: UUID
    created_by: UUID
    validation_status: ValidationStatus
    version: int


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: UUID
    sha256: str | None


@dataclass(frozen=True)
class ValidationResult:
    next_status: ValidationStatus
    next_version: int


def _require_hashes(evidence: list[EvidenceRef]) -> None:
    if not evidence:
        raise ValidationFailedError("At least one hashed evidence item is required")
    for item in evidence:
        digest = (item.sha256 or "").strip().lower()
        if len(digest) != SHA256_LENGTH or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValidationFailedError("Evidence hash is missing or invalid")


def _require_complete_checklist(checklist_version: str, checklist_items: list[dict]) -> None:
    if checklist_version != CHECKLIST_VERSION:
        raise ValidationFailedError("checklist version is not the active credit-legality checklist")
    by_code = {item["code"]: bool(item.get("satisfied")) for item in checklist_items}
    missing = [code for code in required_item_codes() if not by_code.get(code)]
    if missing:
        raise ValidationFailedError("checklist is incomplete for approval")


def decide_validation(
    *,
    credit: CreditSnapshot,
    actor_id: UUID,
    role: Role,
    decision: Decision,
    checklist_version: str,
    checklist_items: list[dict],
    evidence: list[EvidenceRef],
) -> ValidationResult:
    if role != Role.VALIDATOR:
        raise ForbiddenError("Only a validator role may record a credit validation")
    if actor_id == credit.created_by:
        raise ForbiddenError("Credit creator cannot validate the same finding (segregation)")
    if credit.validation_status not in OPEN_STATUSES:
        raise ConflictError("Invalid validation transition for the current credit state")
    _require_hashes(evidence)
    if decision is Decision.APPROVE:
        _require_complete_checklist(checklist_version, checklist_items)
    elif checklist_version != CHECKLIST_VERSION:
        raise ValidationFailedError("checklist version is not the active credit-legality checklist")
    return ValidationResult(
        next_status=DECISION_TO_STATUS[decision],
        next_version=credit.version + 1,
    )
