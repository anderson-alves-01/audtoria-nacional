# Plan — Ativação PE ICMS/IPVA (CSV oficial)

- Goal: Ativar ingestão técnica da quota ICMS/IPVA de Pernambuco via CSV PUBLIC_OPEN, com fixture mínima, join IBGE7 por nome+UF, lineage Gold e shell atualizado.
- Phase: F3.2 — F3-STATE-ICMS-ACTIVATION, F3-STATE-IPVA-ACTIVATION
- Spec: ROADMAP 1.2, `contracts/sources/official-catalog.yaml`, `contracts/sources/state-transfers-catalog.yaml`
- Components/files:
  - `apps/api/.../adapters/ingest/parsers.py` — `parse_state_pe_csv`
  - `apps/api/.../application/official_ingest.py` — registrar conector `state_pe_csv`
  - `apps/api/.../domain/gold.py` — presentation ESTADO-ICMS/IPVA
  - `apps/api/.../domain/state_transfers.py` — PE `ingestAllowed=true`
  - `contracts/sources/*` — PE TECHNICALLY_APPROVED
  - `tests/fixtures/official-snapshots/pe-transferencias-municipais-2024.csv`
  - testes unit/integration + UI spec
  - migration `0028_state_pe_activation` → 0.3.25
- Interfaces: `POST /v1/data-sources/ESTADO-ICMS-QUOTA|/ESTADO-IPVA-QUOTA/ingest`; `GET /v1/state-transfers`
- Data: PUBLIC_OPEN; fixture oficial minimizada só em testes; sem carga estadual completa em runtime
- Security: sem crédito/cobrança; fail-closed para demais UFs; BA/MG/RJ sem ingest
- Migration: aditiva meta 0.3.25; rollback downgrade 0028→0027
- Acceptance: parser join IBGE7; IPVA zero publicado; ingest PE 200 com lineage; demais UFs bloqueadas; testes verdes; evidência `evidence/releases/0.3.25/`
- Human gates: inalterados; Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
