# Verdict 0.3.71

## Fatia

BCB OLINDA Expectativas Focus anuais: allowlist expandida com
`Dívida líquida do setor público` (PERCENT_OF_GDP, baseCalculo=0) e
`Balança comercial` (`IndicadorDetalhe=Saldo`, USD_BILLION) via multi-fetch
`bcb_olinda_expectativas` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt` / `tests-partial.txt`
- Fonte: PUBLIC_OPEN; fixtures OData mínimas; sem crédito
- Unidades novas: `PERCENT_OF_GDP`, `USD_BILLION`
- Migration: `0074_bcb_olinda_divida_balanca` → implementation_version `0.3.71`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0073_bcb_olinda_pib_sectors` e restringir allowlist
removendo Dívida/Balança no catálogo/runtime; remover `indicator_detalhe`.
