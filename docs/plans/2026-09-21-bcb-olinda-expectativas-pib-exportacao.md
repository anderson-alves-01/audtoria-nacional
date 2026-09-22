# Plan — BCB OLINDA Expectativas PIB Exportação de bens e serviços (0.3.83)

## Objetivo

Ativar indicador Focus anual `PIB Exportação de bens e serviços`
(PERCENT_PER_YEAR, baseCalculo=1) no conector multi-fetch
`bcb_olinda_expectativas`.

## Critérios de aceite

- allowlist + units no catálogo oficial
- fixture OData mínima (8 linhas)
- HTTP helper mapeia URL encoded
- unit parse Mediana=4.2676; silverCount integração=216 (27×8)
- layout `bcb-olinda-expectativas-anuais-v18`
- migration `0086_bcb_olinda_pib_exportacao` → `0.3.83`
- Gold REFERENCE_QUANTITY; sem crédito
- UF re-probe sem ACTIVATE_NOW

## Rollback

Downgrade Alembic para `0085_bcb_olinda_pib_despesa_adm` e remover o indicador
da allowlist no catálogo/runtime.
