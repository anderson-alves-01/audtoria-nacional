# Plan — BCB OLINDA Expectativas Produção industrial (0.3.85)

## Objetivo

Ativar indicador Focus anual `Produção industrial`
(PERCENT_PER_YEAR, baseCalculo=1) no conector multi-fetch
`bcb_olinda_expectativas`.

Nota: série oficial com última publicação em 2021-09-13; ainda PUBLIC_OPEN
e fetchável. Documentar staleness na evidência; não inventar dados recentes.

## Critérios de aceite

- allowlist + units no catálogo oficial
- fixture OData mínima (8 linhas)
- HTTP helper mapeia URL encoded
- unit parse Mediana da primeira linha (6.3348); silverCount integração=232 (29×8)
- layout `bcb-olinda-expectativas-anuais-v20`
- migration `0088_bcb_olinda_prod_ind` → `0.3.85`
- Gold REFERENCE_QUANTITY; sem crédito
- UF re-probe sem ACTIVATE_NOW
- próximo OLINDA: IPCA-15 (baseCalculo=0)

## Rollback

Downgrade Alembic para `0087_bcb_olinda_pib_importacao` e remover o indicador
da allowlist no catálogo/runtime.
