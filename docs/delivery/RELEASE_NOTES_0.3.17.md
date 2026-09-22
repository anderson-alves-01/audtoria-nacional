# Release notes 0.3.17

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Nesta fatia

- `GET /v1/diagnosis` — diagnóstico municipal técnico vazio (`recoveryMeta=null`, checklist unmet, G1 BLOCKED, commandsDisabled).
- `GET /v1/audit-rules` — catálogo de regras não vinculantes (`createsTaxCredit=false`, `taxPotentialAsCredit=false`, G4 ausente).
- Telas `/diagnostico` e `/regras-auditoria` com estados loading/empty/ok/erro.
- Calendário IBS/CBS `catalog-official-docs-v1` com `preservedDocuments` (lineage Gold EC132/LC214) e item `LC-214-2025`; binding/operational/homologated permanecem false.
- Fonte `SICONFI-RGF` via conector `siconfi_statement` (fixture, lineage, dashboard financeiro).
- Segurança local: MFA obrigatório fora de `local`, DLP de prompt, auditoria `tool.*`, rejeição de secrets embutidos em ambientes não locais.
- Backup/restore Postgres local com dry-run (`scripts/postgres-backup*`, `scripts/postgres-restore*`) e runbook.

## Não concluído

Backfill nacional, fontes estaduais estruturadas, território RFB, dados municipais reais, piloto, produção e homologação humana.
