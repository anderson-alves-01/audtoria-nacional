# Verdict 0.3.74

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida com
`Dívida bruta do governo geral` (PERCENT_OF_GDP, baseCalculo=0) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt`
- Fonte: PUBLIC_OPEN; fixture OData mínima; sem crédito
- Layout `bcb-olinda-expectativas-anuais-v9`; silverCount 128 (16×8)
- Migration: `0077_bcb_olinda_divida_bruta` → implementation_version `0.3.74`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0076_bcb_olinda_resultado_nom` e restringir
allowlist removendo Dívida bruta do governo geral no catálogo/runtime.
