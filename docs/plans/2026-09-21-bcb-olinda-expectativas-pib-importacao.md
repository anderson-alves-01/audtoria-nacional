# Plan — BCB OLINDA Expectativas PIB Importação de bens e serviços (0.3.84)

## Objetivo

Ativar indicador Focus anual `PIB Importação de bens e serviços`
(PERCENT_PER_YEAR, baseCalculo=1) no conector multi-fetch
`bcb_olinda_expectativas`.

## Critérios de aceite

- allowlist + units no catálogo oficial
- fixture OData mínima (8 linhas)
- HTTP helper mapeia URL encoded
- unit parse Mediana da primeira linha; silverCount integração=224 (28×8)
- layout `bcb-olinda-expectativas-anuais-v19`
- migration `0087_bcb_olinda_pib_importacao` → `0.3.84`
- Gold REFERENCE_QUANTITY; sem crédito
- UF re-probe sem ACTIVATE_NOW

## Rollback

Downgrade Alembic para `0086_bcb_olinda_pib_exportacao` e remover o indicador
da allowlist no catálogo/runtime.
