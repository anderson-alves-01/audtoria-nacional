# Ciclo 2026-09-21 — BCB OLINDA IPCA-15

## Fatia

`IPCA-15` (PERCENT_PER_YEAR, baseCalculo=0) via multi-fetch
`bcb_olinda_expectativas` (PUBLIC_OPEN).

## Alterações

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`IPCA-15`
- `indicator_base_calculo.IPCA-15=0` (base=1 vazio na fonte)
- Layout `bcb-olinda-expectativas-anuais-v21`; silverCount 240
- Próximo OLINDA: IPC-Fipe / IPA-M / IPA-DI

## Rollback

`IPCA-15` da allowlist no catálogo/runtime; Alembic → `0088_bcb_olinda_prod_ind`.
