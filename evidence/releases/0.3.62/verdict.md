# Verdict 0.3.62

## Fatia

Tesouro mensal allowlist FUNDEB complement (`TESOURO-FUNDEB-COMPLEMENT-VALORES`):
COUN VAAT/VAAR/VAAF + AJUSTE FUNDEB VAAT no CSV CKAN PUBLIC_OPEN.

## Evidência

- Unit + integration (official ingest, gold invariants, dashboards): ver `tests.txt`
- Fonte: PUBLIC_OPEN; fixture mínima; sem crédito
- Modalidades: `FDB_COMP_TO_FUNDEB`, `FDB_COMP_TO_AJUSTE_FUNDEB`
- Migration: `0065_tesouro_fundeb_complement` → implementation_version `0.3.62`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0064_state_rs_compensacao_lc194` e remover a fonte
`TESOURO-FUNDEB-COMPLEMENT-VALORES` do catálogo/runtime.
