# Plan — BCB OLINDA Expectativas IPCA Administrados + Alimentação (0.3.78)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` com `IPCA Administrados` e
`IPCA Alimentação no domicílio` (`PERCENT_PER_YEAR`, baseCalculo=1),
PUBLIC_OPEN, REFERENCE_QUANTITY.

## Escopo

- catálogo allowlist + units + layout v13
- fixtures OData mínimas + HTTP helper
- testes unit/integration (silverCount=176 = 22×8)
- migration `0081_bcb_olinda_ipca_admin` → `0.3.78`
- evidência + fila + estado
- UF re-probe (sem ACTIVATE_NOW esperado)

## Fora de escopo

Homologação humana; UF restantes sem tabular estável; carga nacional;
`IPCA Bens industrializados` (próximo ciclo se priorizado).
