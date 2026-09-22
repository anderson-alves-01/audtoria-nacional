# Plan — BCB OLINDA Expectativas PIB Despesa de consumo da administração pública (0.3.82)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` com `PIB Despesa de consumo da administração pública`
(`PERCENT_PER_YEAR`, baseCalculo=1), PUBLIC_OPEN, REFERENCE_QUANTITY.

## Escopo

- catálogo allowlist + units + layout v17
- fixture OData mínima + HTTP helper (`PIB%20Despesa%20de%20consumo%20da%20administra%C3%A7%C3%A3o%20p%C3%BAblica`)
- testes unit/integration (silverCount=208 = 26×8)
- migration `0085_bcb_olinda_pib_despesa_adm` → `0.3.82`
- evidência + fila + estado
- UF re-probe (sem ACTIVATE_NOW; reaproveita status 0.3.81)

## Fora de escopo

Homologação humana; UF restantes sem tabular estável; carga nacional;
outros indicadores Focus ainda fora da allowlist (próximo: PIB Exportação de bens e serviços).
