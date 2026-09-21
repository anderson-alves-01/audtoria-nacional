# Plan — BCB OLINDA Expectativas IPCA-15 (0.3.86)

## Objetivo

Ativar indicador Focus anual `IPCA-15`
(PERCENT_PER_YEAR, baseCalculo=0) no conector multi-fetch
`bcb_olinda_expectativas`.

Nota: série oficial com última publicação em 2021-02-17; ainda PUBLIC_OPEN
e fetchável. Documentar staleness na evidência; não inventar dados recentes.
baseCalculo=1 retorna zero linhas na fonte; override obrigatório =0.

## Critérios de aceite

- allowlist + units + `indicator_base_calculo.IPCA-15=0` no catálogo oficial
- fixture OData mínima (8 linhas)
- HTTP helper mapeia URL encoded com baseCalculo=0
- unit parse Mediana da primeira linha (3.79); silverCount integração=240 (30×8)
- layout `bcb-olinda-expectativas-anuais-v21`
- migration `0089_bcb_olinda_ipca15` → `0.3.86`
- Gold REFERENCE_QUANTITY; sem crédito
- UF re-probe sem ACTIVATE_NOW
- próximo OLINDA: IPC-Fipe / IPA-M / IPA-DI

## Rollback

Downgrade Alembic para `0088_bcb_olinda_prod_ind` e remover o indicador
da allowlist no catálogo/runtime.
