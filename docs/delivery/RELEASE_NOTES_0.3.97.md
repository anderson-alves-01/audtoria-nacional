# Release notes 0.3.97

## Summary

Activate BCB OLINDA `ExpectativasMercadoInflacao12Meses` and
`ExpectativasMercadoInflacao24Meses` as PUBLIC_OPEN reference enrichment,
distinct from annual/monthly/trimestral Focus and from Selic Copom.

## Technical

- Sources: `BCB-OLINDA-EXPECTATIVAS-INFLACAO-12M`, `BCB-OLINDA-EXPECTATIVAS-INFLACAO-24M`
- Connector: `bcb_olinda_expectativas` with `horizon_field=Suavizada`
- Layouts: `bcb-olinda-expectativas-inflacao12m-v1`, `…-inflacao24m-v1`
- 12m allowlist: IPCA, IGP-M, IPCA Livres, IPCA Serviços; silverCount=8
- 24m allowlist: IPCA, IPCA Livres, IPCA Serviços, IPCA Bens industrializados; silverCount=8
- baseCalculo=1; max_rows=8 per indicator; unit PERCENT_PER_YEAR
- Migration: `0100_bcb_olinda_inflacao_12_24m` → `0.3.97`

## Out of scope

- ExpectativasMercadoTop5*
- Remaining UF tabular activations (RJ IP-blocked, SP HTML-only, etc.)
