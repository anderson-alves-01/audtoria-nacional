# 0.3.12 — stub Tesouro sintético e checklists G0/G1 bloqueados

## Goal and user outcome

Ingerir fixture sintético `TESOURO-TRANSPARENTE` pelo mesmo framework de catálogo, sem conector oficial e sem crédito. Expor checklists G0/G1 na API e na UI, todos unmet, sem fabricar aprovação.

## Roadmap phase and epic

F3.1 local (Tesouro stub) + G0/G1 interface BLOCKED. G7 oficial permanece OFFICIAL_BLOCKED.

## Approved specification

- ROADMAP 1.2 F3.1, G7 (ocorrência local ≠ conector oficial), G0/G1.
- Fonte pública/oficial de catálogo não constitui crédito.
- Feature flags `official_tesouro_connectors` e `real_data_ingestion` permanecem false.

## Components

- `pipelines/synthetic/tesouro_transparente_2026_01.json`
- `application/source_ingest.py` FIXTURES
- `domain/gates.py` checklists G0/G1 unmet
- `GET /v1/program-gates` (campos extras, compatível)
- Angular `/gates`
- Alembic `0014` version bump 0.3.12

## Security

Ingestão: `tech_admin`. Leitura: papéis fiscais. Sem download de base Tesouro. Sem marcar G0/G1 GO.

## Migration

`0014_tesouro_stub_gates` aditivo (`create_all` + schema_meta 0.3.12). Sem tabela nova obrigatória.

## Acceptance

- TESOURO ingest: silver/quarantine, replay, `taxCreditCreated=false`, `wouldDownloadFullBase=false`, `sourceRole=OFFICIAL_TRANSFER`
- G0 e G1 `status=BLOCKED`, todos os itens de checklist `met=false`, `humanApprovalFabricated=false`
- UI `/gates` mostra BLOCKED e não oferece botão de aprovar
- Flags oficiais false

## Evidence

`evidence/releases/0.3.12/`

## Human gates

G0/G1/G7 oficial: BLOCKED. Este stub não autoriza conector Tesouro.
