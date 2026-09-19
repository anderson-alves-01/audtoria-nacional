from sirta_api.domain.audit_cases import (
    AUDIT_CASES_VERSION,
    build_audit_cases_page,
    reject_audit_case_create,
)
from sirta_api.domain.errors import ConflictError


def test_audit_cases_page_is_empty_and_never_credit() -> None:
    assert AUDIT_CASES_VERSION.startswith("audit-cases-technical-")
    page = build_audit_cases_page()
    assert page["binding"] is False
    assert page["commandsDisabled"] is True
    assert page["createsTaxCredit"] is False
    assert page["legalCommandsEnabled"] is False
    assert page["items"] == []
    assert page["g5Status"] == "BLOCKED"


def test_reject_audit_case_create_raises_conflict() -> None:
    try:
        reject_audit_case_create()
        raise AssertionError("expected ConflictError")
    except ConflictError as exc:
        assert exc.status == 409
        assert "desativada" in exc.detail.lower() or "desativado" in exc.detail.lower()
