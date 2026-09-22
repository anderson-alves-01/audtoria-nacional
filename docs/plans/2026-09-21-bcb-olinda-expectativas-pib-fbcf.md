# Plan — BCB OLINDA Expectativas PIB Formação Bruta de Capital Fixo (0.3.80)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` com `PIB Formação Bruta de Capital Fixo`
(`PERCENT_PER_YEAR`, baseCalculo=1), PUBLIC_OPEN, REFERENCE_QUANTITY.

## Escopo

- catálogo allowlist + units + layout v15
- fixture OData mínima + HTTP helper (`PIB%20Forma%C3%A7%C3%A3o%20Bruta%20de%20Capital%20Fixo`)
- testes unit/integration (silverCount=192 = 24×8)
- migration `0083_bcb_olinda_pib_fbcf` → `0.3.80`
- evidência + fila + estado
- UF re-probe (sem ACTIVATE_NOW; reaproveita status 0.3.79)

## Fora de escopo

Homologação humana; UF restantes sem tabular estável; carga nacional;
outros indicadores Focus ainda fora da allowlist.
