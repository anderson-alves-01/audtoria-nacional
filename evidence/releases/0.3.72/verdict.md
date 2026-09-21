# Verdict 0.3.72

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida com
`Resultado primário` (PERCENT_OF_GDP, baseCalculo=1) e `Conta corrente`
(USD_BILLION, baseCalculo=1) via multi-fetch `bcb_olinda_expectativas`
(PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt` / `tests-partial.txt`
- Fonte: PUBLIC_OPEN; fixtures OData mínimas; sem crédito
- Layout `bcb-olinda-expectativas-anuais-v7`; silverCount 112 (14×8)
- Migration: `0075_bcb_olinda_resultado_conta` → implementation_version `0.3.72`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0074_bcb_olinda_divida_balanca` e restringir
allowlist removendo Resultado primário / Conta corrente no catálogo/runtime.
