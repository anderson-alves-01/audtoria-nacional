# Plan — BCB OLINDA Expectativas IPCA Livres + IPCA Serviços (0.3.77)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` com `IPCA Livres` e `IPCA Serviços`
(`PERCENT_PER_YEAR`, baseCalculo=1), PUBLIC_OPEN, REFERENCE_QUANTITY.

## Escopo

- catálogo allowlist + units + layout v12
- fixtures OData mínimas + HTTP helper
- testes unit/integration (silverCount=160 = 20×8)
- migration `0080_bcb_olinda_ipca_livres` → `0.3.77`
- evidência + fila + estado
- UF re-probe (sem ACTIVATE_NOW esperado)

## Fora de escopo

Homologação humana; UF restantes sem tabular estável; carga nacional;
IPCA Administrados (próximo ciclo se priorizado).
