from uuid import uuid4

import pytest

from sirta_api.domain.credit import (
    CHECKLIST_VERSION,
    CreditSnapshot,
    Decision,
    EvidenceRef,
    ValidationStatus,
    decide_validation,
)
from sirta_api.domain.errors import ConflictError, ForbiddenError, ValidationFailedError
from sirta_api.domain.identities import Role

CREDIT_ID = uuid4()
CREATOR = uuid4()
VALIDATOR = uuid4()
SHA = "a" * 64


def _credit(status: ValidationStatus = ValidationStatus.IDENTIFIED, version: int = 1) -> CreditSnapshot:
    return CreditSnapshot(
        credit_id=CREDIT_ID,
        created_by=CREATOR,
        validation_status=status,
        version=version,
    )


def _items(complete: bool = True) -> list:
    from sirta_api.domain.checklist import required_item_codes

    return [
        {"code": code, "satisfied": complete}
        for code in required_item_codes()
    ]


def _evidence() -> list[EvidenceRef]:
    return [EvidenceRef(evidence_id=uuid4(), sha256=SHA)]


def _decide(*, role=Role.VALIDATOR, actor=VALIDATOR, decision=Decision.APPROVE, status=ValidationStatus.IDENTIFIED, items=None, evidence=None):
    return decide_validation(
        credit=_credit(status),
        actor_id=actor,
        role=role,
        decision=decision,
        checklist_version=CHECKLIST_VERSION,
        checklist_items=items if items is not None else _items(),
        evidence=evidence if evidence is not None else _evidence(),
    )


def test_approve_identified_credit_becomes_validated() -> None:
    result = _decide()
    assert result.next_status == ValidationStatus.VALIDATED
    assert result.next_version == 2


def test_request_information_moves_to_under_review() -> None:
    result = _decide(decision=Decision.REQUEST_INFORMATION)
    assert result.next_status == ValidationStatus.UNDER_REVIEW


def test_reject_identified_credit() -> None:
    result = _decide(decision=Decision.REJECT)
    assert result.next_status == ValidationStatus.REJECTED


def test_approve_from_under_review() -> None:
    result = _decide(status=ValidationStatus.UNDER_REVIEW)
    assert result.next_status == ValidationStatus.VALIDATED


@pytest.mark.parametrize(
    "status",
    [ValidationStatus.VALIDATED, ValidationStatus.REJECTED, ValidationStatus.CANCELLED],
)
def test_terminal_status_cannot_transition(status: ValidationStatus) -> None:
    try:
        _decide(status=status)
    except ConflictError as exc:
        assert exc.status == 409
        return
    raise AssertionError("expected ConflictError")


def test_analyst_cannot_validate() -> None:
    try:
        _decide(role=Role.ANALYST)
    except ForbiddenError as exc:
        assert "validator" in exc.detail.lower() or "role" in exc.detail.lower()
        return
    raise AssertionError("expected ForbiddenError")


def test_creator_cannot_validate_own_credit() -> None:
    try:
        _decide(actor=CREATOR)
    except ForbiddenError as exc:
        assert "creator" in exc.detail.lower() or "segregat" in exc.detail.lower()
        return
    raise AssertionError("expected ForbiddenError")


def test_incomplete_checklist_blocks_approve() -> None:
    try:
        _decide(items=_items(complete=False))
    except ValidationFailedError as exc:
        assert "checklist" in exc.detail.lower()
        return
    raise AssertionError("expected ValidationFailedError")


def test_evidence_without_hash_is_rejected() -> None:
    try:
        _decide(evidence=[EvidenceRef(evidence_id=uuid4(), sha256=None)])
    except ValidationFailedError as exc:
        assert "hash" in exc.detail.lower()
        return
    raise AssertionError("expected ValidationFailedError")
