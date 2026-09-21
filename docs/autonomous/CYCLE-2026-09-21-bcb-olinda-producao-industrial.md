# Ciclo 2026-09-21 — BCB OLINDA Produção industrial

## Entrega

`Produção industrial` (PERCENT_PER_YEAR, baseCalculo=1) via multi-fetch
`bcb_olinda_expectativas`. Série Focus Anuais com última Data=2021-09-13
(congelada na fonte; ainda PUBLIC_OPEN).

## Mudanças

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`Produção industrial`
- Fixture + HTTP helper + unit/integration (silverCount=232)
- Layout v20; silverCount 232 (29×8); migration `0088_bcb_olinda_prod_ind` → `0.3.85`
- Próximo OLINDA: IPCA-15 (baseCalculo=0)

## Rollback

Downgrade Alembic para `0087_bcb_olinda_pib_importacao` e remover
`Produção industrial` da allowlist no catálogo/runtime.
