# 0.3.11 — ingestão sintética guiada pelo catálogo (F3.1)

## Goal and user outcome

Promover um fixture IBGE/SIDRA sintético de Landing até Gold de enriquecimento, com checksum, quarentena e idempotência. Não cria `TaxCredit` e não baixa base oficial.

## Roadmap phase and epic

Fase 3.1 local. G3 oficial e G0/G1 permanecem BLOCKED.

## Approved specification

- ROADMAP 1.2 F3.1 e §15.4 (registrar fonte, preservar checksum, não promover sem contrato).
- Fonte pública não constitui crédito.
- Skill data-engineer: dry-run, resume, quarantine, logical rollback via `published=false`.

## Components

- `pipelines/synthetic/ibge_sidra_2026_01.json`
- `application/source_ingest.py`
- `POST /v1/data-sources/{sourceId}/ingest` (tech_admin)
- `GET /v1/indicators/source-enrichment`
- `gold_enrichments` (migration `0013`)

## Security

Ingestão: `tech_admin`. Leitura Gold: papéis fiscais. `RESTRICTED` 403. Logs sem payloads completos de linha.

## Migration

`0013_source_ingest` aditivo (`create_all` + schema_meta 0.3.11).

## Acceptance

- IBGE: 2 silver, 1 quarentena, replay não duplica, `taxCreditCreated=false`
- Municipal ISS restricted: 403
- Analyst: 403 no ingest; 200 no Gold
- Rollback lógico despublica Gold de enriquecimento

## Evidence

`evidence/releases/0.3.11/`

## Human gates

G0/G1/G3 oficial, download de SIDRA real: BLOCKED.
