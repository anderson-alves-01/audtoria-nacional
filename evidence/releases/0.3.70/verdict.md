# Verdict 0.3.70

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida para IPCA + Selic +
Câmbio + PIB Total + PIB Serviços + PIB Agropecuária + PIB Indústria +
IGP-M + IGP-DI + INPC via multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt` / `tests-partial.txt`
- Fonte: PUBLIC_OPEN; fixtures OData mínimas; sem crédito
- Unidades PIB setoriais: `PERCENT_PER_YEAR`; baseCalculo=1
- Migration: `0073_bcb_olinda_pib_sectors` → implementation_version `0.3.70`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0072_bcb_olinda_igp_inpc` e restringir allowlist
removendo PIB Agropecuária/PIB Indústria no catálogo/runtime.
