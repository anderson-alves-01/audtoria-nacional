# Sprint 2 0.3.2 verification

Date: 2026-09-18
spec_version: 0.3.0
implementation_version: 0.3.2
release_stage: S2_CREDIT_VALIDATION

## Commands

- `python -m pytest tests -q` → 48 passed
- `python -m ruff check apps tests alembic`
- `python -m openapi_spec_validator contracts/openapi/sirta-v1.yaml`
- `python -m alembic upgrade head` → `0004_s2_validation`
- `npm --prefix apps/web test` → 8 SUCCESS

## Acceptance map

| Criterion | Evidence |
|---|---|
| APPROVE IDENTIFIED → VALIDATED | tests/integration/test_validate_credit.py |
| Incomplete checklist 422, no mutation | test_incomplete_checklist_does_not_mutate_credit |
| Terminal state 409, version unchanged | test_second_approval_is_conflict_without_version_change |
| Idempotency replay | test_idempotent_retry_replays_without_second_transition |
| Evidence SHA-256 | tests/integration/test_evidence.py |
| Analyst/creator 403 | test_analyst_cannot_validate, test_creator_cannot_validate_own_credit |
| Cross-tenant 404 | test_cross_tenant_validation_is_hidden |
| Collection still 404 | tests/security/test_isolation.py |
| Audit without rationale/amounts | tests/integration/test_audit.py |

## Cloud / real data / paid

None used.

## Verdicts

- Sprint 2 technical local: GO
- Independent security/fiscal review: BLOQUEADO (implementer cannot self-approve)
- G0 municipal: NO-GO
- Sprint 3 collection: NO-GO until new authorization
- Cloud / real data / production: BLOQUEADO
