# Verdict 0.3.69

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida para IPCA + Selic +
Câmbio + PIB Total + PIB Serviços + IGP-M + IGP-DI + INPC via multi-fetch
`bcb_olinda_expectativas` com `indicator_base_calculo` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt` / `tests-partial.txt`
- Fonte: PUBLIC_OPEN; fixtures OData mínimas; sem crédito
- Unidades: todos `PERCENT_PER_YEAR` (exceto Câmbio=`BRL_PER_USD`)
- IGP-M baseCalculo=1; IGP-DI/INPC baseCalculo=0
- Migration: `0072_bcb_olinda_igp_inpc` → implementation_version `0.3.69`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0071_bcb_olinda_pib` e restringir allowlist
a IPCA/Selic/Câmbio/PIB Total/PIB Serviços no catálogo/runtime.
