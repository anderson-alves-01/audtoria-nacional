# Verdict 0.3.67

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida para IPCA + Selic +
Câmbio via multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt` / `tests-partial.txt`
- Fonte: PUBLIC_OPEN; fixtures OData mínimas; sem crédito
- Unidades: IPCA/Selic=`PERCENT_PER_YEAR`; Câmbio=`BRL_PER_USD`
- Distinto de `BCB-SGS-OLINDA` (REST SGS)
- Migration: `0070_bcb_olinda_selic_cambio` → implementation_version `0.3.67`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0069_bcb_olinda_expectativas` e restringir allowlist
a IPCA no catálogo/runtime.
