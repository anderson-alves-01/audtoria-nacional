# Verdict 0.3.64

## Fatia

Tesouro COINT LC 87/96 por município (`TESOURO-LC87-VALORES`) via conector
`tesouro_coint_municipio_csv` (PUBLIC_OPEN, série histórica ≤2018).

## Evidência

- Unit + integration: ver `tests.txt`
- Fonte: PUBLIC_OPEN; fixture mínima latin-1; sem crédito
- Modalidade: `LC87_RECEIVED`
- Distinto de `TESOURO-LC176-VALORES` (CSV mensal)
- Migration: `0067_tesouro_lc87_coint` → implementation_version `0.3.64`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0066_tesouro_fundeb_coint` e remover a fonte
`TESOURO-LC87-VALORES` do catálogo/runtime.
