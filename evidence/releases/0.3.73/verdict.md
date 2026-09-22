# Verdict 0.3.73

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida com
`Resultado nominal` (PERCENT_OF_GDP, baseCalculo=1) via multi-fetch
`bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt`
- Fonte: PUBLIC_OPEN; fixture OData mínima; sem crédito
- Layout `bcb-olinda-expectativas-anuais-v8`; silverCount 120 (15×8)
- Migration: `0076_bcb_olinda_resultado_nom` → implementation_version `0.3.73`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0075_bcb_olinda_resultado_conta` e restringir
allowlist removendo Resultado nominal no catálogo/runtime.
