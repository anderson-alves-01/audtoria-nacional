# Plano de implementação v0.3

## Objetivo

Entregar um núcleo local executável do SIRTA com dados sintéticos, estados do crédito, validação obrigatória, autorização mínima e contratos estáveis.

## Sprint 0 - Baseline

- Criar workspace backend, frontend e workers.
- Docker Compose com PostgreSQL, Redis, Keycloak e storage compatível.
- Health/readiness, logs JSON e tracing.
- CI sem credenciais de nuvem.
- Seed exclusivamente sintético.

Gate: build reproduzível e ambiente local documentado.

## Sprint 1 - Tenant, território e finalidade

- Organization, Tenant, Territory, User, Role e AccessPurpose.
- Middleware de contexto obrigatório.
- RBAC + ABAC inicial.
- Testes cross-tenant e finalidade ausente.

Gate: nenhuma consulta sensível sem contexto completo.

## Sprint 2 - Crédito e validação

- TaxCredit e estados ortogonais.
- Evidências e hashes.
- Checklist de validação.
- Comando ValidateCredit.
- Auditoria imutável.

Gate: transições inválidas falham sem alteração parcial.

## Sprint 3 - Cobrança controlada

- CollectionCase e StartAdministrativeCollection.
- Bloqueio de crédito não validado, suspenso ou impedido.
- Timeline e SLA.
- API e telas mínimas.

Gate: regra “nenhuma cobrança sem validação” comprovada por testes negativos.

## Sprint 4 - Dados e painel mínimo

- Manifesto de carga sintética.
- Bronze/Silver/Gold local.
- Qualidade e quarentena.
- KPIs identificados, auditados, validados e em cobrança.
- Metodologia junto ao indicador.

Gate: reexecução idempotente e números reconciliados.

## Saída v0.3

Aplicação local demonstrável, OpenAPI validada, testes e evidências; nenhuma integração real, nuvem ou produção.

Extensão local 2026 (G6–G8 sintético) está em `current-state.yaml` e `docs/delivery/HUMAN-GATES.md`. Gates G0, G1, G4, G7 oficial, G8 oficial, G9 e G10 permanecem humanos.

