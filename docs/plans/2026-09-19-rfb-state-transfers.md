# Plan — RFB territorial + state ICMS/IPVA provenance

- Goal: Complete RFB CNPJ technical connector (resume, manifesto, territorial filter, EI policy) without national load; register RJ structured CSV provenance for state quotas; empty state-transfers shell.
- Phase: F3.2 — F3-RFB-CNPJ, F3-STATE-ICMS-ACTIVATION, F3-STATE-IPVA-ACTIVATION
- Spec: ROADMAP 1.2, official-catalog, state-transfers-catalog
- Data: PUBLIC_OPEN; minimized RFB fixture in tests only; no national RFB download; RJ CSV download IP-blocked in this runtime
- Security: fail-closed without territorial_scope; EI out of Gold; no tax credit
- Migration: additive `0027_rfb_state_transfers` → 0.3.24
- Rollback: alembic downgrade 0027→0026; revert catalog/API/web
- Acceptance: RFB unit tests green; ingest RFB still 403; state-transfers empty API/UI; RJ PROVENANCE_VERIFIED; CI green
- Human gates: unchanged; Gold homologation not requested
