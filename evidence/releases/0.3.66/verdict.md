# Verdict 0.3.66

## Fatia

BCB OLINDA Expectativas Focus anuais (IPCA) via `bcb_olinda_expectativas`
(PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt`
- Fonte: PUBLIC_OPEN; fixture OData mínima; sem crédito
- Distinto de `BCB-SGS-OLINDA` (REST SGS)
- Migration: `0069_bcb_olinda_expectativas` → implementation_version `0.3.66`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0068_tesouro_coint_remaining` e remover
`BCB-OLINDA-EXPECTATIVAS` do catálogo/runtime.
