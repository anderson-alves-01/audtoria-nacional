# Plan — F7/F9/F10 technical shells (0.3.20)

## Goal

Deliver empty but functional technical capacity for transfer reconciliation (F7),
pilot readiness checklist (F9) and local ops governance (F10), without fabricating
human approvals or inventing recovery/credit values.

## Roadmap

- Phase F7 / D9, F9 / D1, F10 / D1
- Queue items: `F7-TRANSFER-RECONCILIATION`, `F9-PILOT-TECHNICAL`, `F10-OPS-GOVERNANCE`

## Spec / ADR

- ROADMAP 1.2 § Fase 7–10
- Transfer skill: differences create occurrence, never tax credit
- AGENTS.md: no real municipal data; fail closed; empty shells OK

## Components / files

- Domain/application/entrypoints: `transfer_reconciliation`, `pilot_readiness`, `ops_governance`
- OpenAPI `contracts/openapi/sirta-v1.yaml`
- Angular: `/conciliacao-transferencias`, `/prontidao` (dedicated), `/operacao-governanca`
- Migration meta `0023_f7_f9_f10_shells` → 0.3.20
- Runbooks under `docs/operations/`
- Evidence `evidence/releases/0.3.20/`

## Interfaces

- `GET/POST /v1/transfer-reconciliation` (POST → 409)
- `GET /v1/pilot-readiness`
- `GET /v1/ops-governance`

## Data classification

- PUBLIC_OPEN references only when both sides exist later; this slice returns empty
- No RESTRICTED municipal samples
- Fixtures: none required beyond unit/integration empty assertions

## Security

- Fiscal read authorization; tech admin denied on read where peer panels deny
- Audit events on get / rejected command
- `canApprove=false`, `canDeploy=false`, G9/G10 BLOCKED

## Migration / rollback

- Additive schema_meta only; downgrade restores 0.3.19

## Acceptance

- Empty panels with disabled commands
- Diff never creates tax credit
- Pilot checklist technical + G9 BLOCKED
- Ops runbooks listed; G10 BLOCKED
- Unit, integration, Angular tests green

## Human gates

- G7 official, G9, G10 remain BLOCKED / OFFICIAL_BLOCKED
