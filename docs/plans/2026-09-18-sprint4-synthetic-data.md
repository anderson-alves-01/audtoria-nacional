# Sprint 4 — plataforma de dados sintética e funil (0.3.4)

## Goal and user outcome

Publicar um funil local de créditos (identificados, validados, em cobrança) a partir de carga ISS sintética Bronze/Silver/Gold, com quarentena de linhas inválidas e reexecução idempotente. Potencial em reais permanece hipótese, fora do KPI.

## Roadmap phase and epic

SPRINT-PLAN Sprint 4; ROADMAP 2026 Fase 3 (G3) local. G4 homologação municipal **não** é reivindicada.

## Approved specification

DATA-PLATFORM.md, invariante 8 (transferência/potencial não vira TaxCredit), REGIONAL-PLAN hipóteses.

## Components

`pipelines/synthetic/iss_2026_01.json`, models load/bronze/silver/gold/quarantine, `application/pipeline.py`, `GET /v1/indicators/credit-funnel`, Angular dashboard.

## Security

Contexto F0. GET funil exige leitura fiscal. POST carga: tech_admin (job, sem listar créditos). Logs sem valores de linha.

## Migration

`0006_s4_pipeline` aditivo.

## Acceptance

Reexecução mesmo checksum não duplica; linha inválida QUARANTINED não entra Gold; totais Gold = contagens de tax_credits do tenant; rollback lógico despublica.

## Human gates

G4 especialista municipal, dado real, G0: BLOQUEADO.
