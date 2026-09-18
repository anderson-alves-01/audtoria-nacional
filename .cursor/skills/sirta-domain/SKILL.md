---
name: sirta-domain
description: Implement or review municipal tax-credit validation, collection, installment, active-debt and recovery behavior.
---
# SIRTA Domain

Read `docs/product/SIRTA-PRODUCT.md`, `docs/product/GLOSSARY.md`, `docs/architecture/SIRTA-DOMAIN.md` and `contracts/openapi/sirta-v1.yaml`.

## Mandatory invariants

- No collection without approved validation.
- Suspended, extinguished or blocked credit cannot advance.
- State dimensions remain orthogonal.
- Every transition is authorized, transactional and audited.
- Recovered value requires payment reconciliation.
- Potential economic value never becomes a credit automatically.

Use strict TDD for domain commands. Test positive path, invalid transition, missing purpose, cross-tenant access, insufficient role and retry/idempotency. Stop for tax or legal interpretation.

