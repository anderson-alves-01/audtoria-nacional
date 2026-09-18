# F0 0.3.1 verification

Date: 2026-09-18
spec_version: 0.3.0
implementation_version: 0.3.1
release_stage: F0_FOUNDATION

## Commands

- `python -m pytest tests -q` → 26 passed (evidence/pytest.txt)
- `python -m ruff check apps tests alembic`
- `python -m openapi_spec_validator contracts/openapi/sirta-v1.yaml`
- `alembic upgrade head` against local Compose Postgres :55432
- `npm --prefix apps/web test` → 4 SUCCESS (ChromeHeadless)
- `npm --prefix apps/web run build`
- `docker build -f apps/api/Dockerfile -t sirta-api:0.3.1 .`
- `docker build -f apps/workers/Dockerfile -t sirta-worker:0.3.1 .`
- `docker build -f apps/web/Dockerfile -t sirta-web:0.3.1 .`

## Acceptance map

| Criterion | Evidence |
|---|---|
| Git + gitignore | commits S0.1+ |
| Compose local stack | compose.yaml, test_compose_local |
| /health 200 | tests/unit/test_health.py |
| /ready 503 if DB down | tests/unit/test_ready.py |
| CI without cloud creds | .github/workflows/ci.yml, test_ci_local |
| Fail-closed context | tests/security/test_isolation.py |
| Cross-tenant 404 | test_cross_tenant_credit_is_hidden |
| tech_admin 403 | test_tech_admin_cannot_read_fiscal_content |
| Isolation tests fail if dependency removed | test_protected_routes_require_access_context_dependency |
| Logs without token/CPF | tests/security/test_logs.py |
| No ValidateCredit/collection | test_validation_and_collection_are_not_implemented |
| Rollback | docs/operations/local-dev.md |

## Cloud / real data / paid resources

None used. Local Docker images, PyPI, npm registry only. No Terraform apply, no GCP/AWS, no municipal data.

## Verdicts

- F0 technical local: GO
- G0 municipal program: NO-GO
- Cloud / real data / production: BLOQUEADO
- Advance beyond F0: NO-GO without new authorization
