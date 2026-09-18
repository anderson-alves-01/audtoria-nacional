# Sprint 2 — crédito, evidências e ValidateCredit (implementation 0.3.2)

## Goal and user outcome

Permitir que um **validador** autorizado registre uma decisão de validação sobre um crédito sintético já identificado, com checklist homologável, evidências com hash e auditoria imutável. Transições inválidas falham com RFC 9457 **409** e **não alteram** o crédito.

Outcome: `POST /v1/tax-credits/{creditId}/validations` com `Idempotency-Key` aprova, rejeita ou pede informação; analista e criador do finding não validam; cobrança continua **não implementada**.

## Roadmap phase and epic

- Roadmap vigente: `docs/delivery/ROADMAP-SIRTA-2026.md`.
- Fase: Sprint 2 de `docs/delivery/SPRINT-PLAN-v0.3.md`.
- Épico: `EP-SIRTA-003` (`SIRTA-020` a `SIRTA-023`).
- `spec_version: 0.3.0` (notas de `RELEASE-v0.3.0.md` intactas).
- `implementation_version: 0.3.2`.
- `release_stage: S2_CREDIT_VALIDATION`.
- Fora de escopo: StartAdministrativeCollection, ISS pipeline, Gold/ISR, G0 municipal, nuvem, dado real.

## Approved specification and ADR references

- Autorização humana de 2026-09-18 para avançar além de F0.
- `docs/architecture/SIRTA-DOMAIN.md` (estados ortogonais, invariantes 3–7).
- `docs/security/ROLE-MATRIX.md` (somente validador valida; criador não aprova o próprio crédito).
- `checklists/CREDIT-LEGALITY.md` (versão `credit-legality-v1`; não é parecer jurídico).
- `contracts/openapi/sirta-v1.yaml`.
- ADR-002, ADR-007.

## Components and exact files

| Componente | Arquivos |
|---|---|
| Plano | `docs/plans/2026-09-18-sprint2-credit-validation.md` |
| Domínio | `apps/api/src/sirta_api/domain/credit.py`, `checklist.py`, `errors.py`, `authorization.py` |
| Aplicação | `apps/api/src/sirta_api/application/validate_credit.py` |
| Persistência | `apps/api/src/sirta_api/adapters/db/models.py`, `seed.py`, `alembic/versions/0004_s2_validation.py` |
| HTTP | `apps/api/src/sirta_api/entrypoints/tax_credits.py`, `main.py` |
| Contrato | `contracts/openapi/sirta-v1.yaml` |
| Testes | `tests/unit/test_credit_validation.py`, `tests/integration/test_validate_credit.py`, `tests/security/test_isolation.py` |
| Web | `apps/web/src/app/validation/**` |
| Evidência | `evidence/releases/0.3.2/` |

## Consumed and produced interfaces

Consumidos: OIDC F0, contexto tenant/território/finalidade, `CreateTaxCredit` existente, checklist `credit-legality-v1`.

Produzidos:

- `POST /v1/tax-credits/{creditId}/validations` (protegido)
- Resposta 200 com crédito atualizado e registro de validação
- 401/403/404/409/422 em `application/problem+json`
- Evento `tax_credit.validate`
- Página Angular mínima de decisão (autorização continua na API)

Não produzidos: `/collection-cases`, ISR, transferências, pipelines.

## Data classification and allowed fixtures

Sintético, local/CI. Evidências `EVIDENCE_ALPHA`/`EVIDENCE_BETA` com SHA-256 de payloads `"synthetic-alpha-evidence"` e `"synthetic-beta-evidence"`. Nenhum CPF/CNPJ real.

## Security and authorization impact

- Default deny. Contexto F0 permanece obrigatório.
- Somente `validator` executa ValidateCredit.
- Criador do crédito (`created_by`) não valida o mesmo crédito.
- `tech_admin` e `analyst` recebem 403.
- Cross-tenant: 404.
- Logs sem token, CPF/CNPJ, valores fiscais ou rationale completo.
- Cobrança permanece 404.

## Migration and rollback strategy

- Alembic aditivo `0004_s2_validation`: `evidences`, `credit_validations`, `idempotency_records`; atualiza `schema_meta`.
- Rollback operacional: `docker compose down -v`.
- Rollback de código: `git revert` da fatia S2.x.

## Acceptance criteria and evidence path

1. Transição IDENTIFIED + APPROVE com checklist completo e hashes → VALIDATED; versão incrementa.
2. REQUEST_INFORMATION → UNDER_REVIEW.
3. REJECT → REJECTED.
4. VALIDATED/REJECTED/CANCELLED + nova decisão → 409, estado e versão inalterados.
5. Checklist incompleto no APPROVE → 422, sem linha de validação.
6. Evidência sem hash → 422.
7. Analista, admin técnico ou criador → 403.
8. Mesma `Idempotency-Key` e corpo → 200 idêntico, sem segunda transição.
9. Mesma chave e corpo diferente → 409.
10. Cobrança continua 404.
11. Evento de auditoria `tax_credit.validate` sem PII.

Evidência: `evidence/releases/0.3.2/`.

## Human gates

- G0 municipal: **NO-GO**.
- Interpretação jurídica do checklist: o município homologa; o código só exige os itens configurados.
- Nuvem, dado real, produção, Sprint 3: **BLOQUEADO** até nova autorização.

## Tasks

### S2.1 Domain transitions

Arquivos: `domain/credit.py`, `tests/unit/test_credit_validation.py`.
Comando: `python -m pytest tests/unit/test_credit_validation.py -q`.
Esperado: RED então GREEN para transições permitidas e negadas.

### S2.2 Evidence hashes and checklist

Arquivos: models, seed, migration 0004, `domain/checklist.py`.
Comando: `python -m pytest tests/integration/test_identity_persistence.py tests/unit/test_credit_validation.py -q` e `alembic upgrade head`.

### S2.3 ValidateCredit API

Arquivos: application use case, router, OpenAPI, ConflictError, idempotency.
Comando: `python -m pytest tests/integration/test_validate_credit.py -q`.

### S2.4 Isolation

Arquivos: `tests/security/test_isolation.py`.
Comando: `python -m pytest tests/security -q`.

### S2.5 Angular validation form

Arquivos: `apps/web/src/app/validation/**`.
Comando: `npm --prefix apps/web test`.

### S2.6 Evidence and state

Atualizar docs, backlog, `current-state.yaml` somente após gates verdes.
