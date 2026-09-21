# Plan — BCB OLINDA Expectativas IPCA Bens industrializados (0.3.79)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` com `IPCA Bens industrializados`
(`PERCENT_PER_YEAR`, baseCalculo=1), PUBLIC_OPEN, REFERENCE_QUANTITY.

## Escopo

- catálogo allowlist + units + layout v14
- fixture OData mínima + HTTP helper (`IPCA%20Bens%20industrializados`)
- testes unit/integration (silverCount=184 = 23×8)
- migration `0082_bcb_olinda_ipca_bens` → `0.3.79`
- evidência + fila + estado
- UF re-probe (sem ACTIVATE_NOW; reaproveita status 0.3.78)

## Fora de escopo

Homologação humana; UF restantes sem tabular estável; carga nacional;
outros indicadores Focus ainda fora da allowlist.
