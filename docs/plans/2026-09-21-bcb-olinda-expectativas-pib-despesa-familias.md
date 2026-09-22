# Plan — BCB OLINDA Expectativas PIB Despesa de consumo das famílias (0.3.81)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` com `PIB Despesa de consumo das famílias`
(`PERCENT_PER_YEAR`, baseCalculo=1), PUBLIC_OPEN, REFERENCE_QUANTITY.

## Escopo

- catálogo allowlist + units + layout v16
- fixture OData mínima + HTTP helper (`PIB%20Despesa%20de%20consumo%20das%20fam%C3%ADlias`)
- testes unit/integration (silverCount=200 = 25×8)
- migration `0084_bcb_olinda_pib_despesa_fam` → `0.3.81`
- evidência + fila + estado
- UF re-probe (sem ACTIVATE_NOW; reaproveita status 0.3.80)

## Fora de escopo

Homologação humana; UF restantes sem tabular estável; carga nacional;
outros indicadores Focus ainda fora da allowlist.
