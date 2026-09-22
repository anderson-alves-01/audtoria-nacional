# Verdict 0.3.68

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida para IPCA + Selic +
Câmbio + PIB Total + PIB Serviços via multi-fetch `bcb_olinda_expectativas`
(PUBLIC_OPEN). Re-probe UF restantes: nenhuma tabular recente.

## Evidência

- Unit + integration: ver `tests.txt` / `tests-partial.txt`
- Fonte: PUBLIC_OPEN; fixtures OData mínimas; sem crédito
- Unidades: IPCA/Selic/PIB*=`PERCENT_PER_YEAR`; Câmbio=`BRL_PER_USD`
- Distinto de `BCB-SGS-OLINDA` (REST SGS)
- Migration: `0071_bcb_olinda_pib` → implementation_version `0.3.68`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0070_bcb_olinda_selic_cambio` e restringir allowlist
a IPCA/Selic/Câmbio no catálogo/runtime.
