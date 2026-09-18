# Sprint 3 — cobrança administrativa controlada (implementation 0.3.3)

## Goal and user outcome

Um cobrador autorizado inicia cobrança administrativa somente sobre crédito sintético **VALIDATED** e **ENFORCEABLE**. Crédito identificado, rejeitado, suspenso, extinto ou bloqueado permanece inalterado (409).

## Roadmap phase and epic

- `docs/delivery/SPRINT-PLAN-v0.3.md` Sprint 3; ROADMAP 2026 Fase 5 / G5 local.
- `spec_version: 0.3.0`, `implementation_version: 0.3.3`, `release_stage: S3_COLLECTION`.
- Fora: G0/G1 municipal, G9/G10, nuvem, dado real, parcelamento (G6).

## Approved specification and ADR references

- SIRTA-DOMAIN invariantes 3 e 4; ROLE-MATRIX (somente papel de cobrança inicia cobrança).
- OpenAPI `startAdministrativeCollection`.

## Components and exact files

`domain/collection.py`, `application/start_collection.py`, models/seed/migration `0005_s3_collection.py`, tax_credits router, OpenAPI, Angular `collection/`, tests unit/integration/security.

## Consumed and produced interfaces

`POST /v1/tax-credits/{creditId}/collection-cases` com Idempotency-Key, tenant/territory/purpose.
`GET /v1/collection-cases`.
Não produz dívida ativa nem parcelamento.

## Data classification and allowed fixtures

Sintético. Usuário `collector.alpha`. CREDIT_ALPHA permanece IDENTIFIED para testes negativos.

## Security and authorization impact

Somente `collector`. Validator/analyst/tech_admin 403. Cross-tenant 404. Fail-closed F0 context. Logs sem valores.

## Migration and rollback strategy

Alembic aditivo 0005. Rollback: `docker compose down -v` e `git revert`.

## Acceptance criteria and evidence path

1. VALIDATED+ENFORCEABLE → ADMINISTRATIVE, caso com SLA e timeline.
2. IDENTIFIED → 409, version unchanged.
3. SUSPENDED/BLOCKED/EXTINGUISHED → 409.
4. Papel insuficiente → 403.
5. Idempotency replay.
6. Auditoria `tax_credit.collect` sem PII.

`evidence/releases/0.3.3/`

## Human gates

G0 municipal, revisão jurídica, produção: BLOQUEADO.
