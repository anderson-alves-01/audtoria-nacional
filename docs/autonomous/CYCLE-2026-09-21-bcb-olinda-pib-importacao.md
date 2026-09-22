# Ciclo 2026-09-21 — BCB OLINDA PIB Importação de bens e serviços

## Fatia

`PIB Importação de bens e serviços` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Entregas

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`PIB Importação de bens e serviços`
- Fixture + HTTP helper + unit/integration (silverCount=224)
- Layout v19; silverCount 224 (28×8); migration `0087_bcb_olinda_pib_importacao` → `0.3.84`
- UF re-probe: nenhum ACTIVATE_NOW

## Rollback

Downgrade Alembic para `0086_bcb_olinda_pib_exportacao` e remover
`PIB Importação de bens e serviços` da allowlist no catálogo/runtime.

CYCLE_RESULT=PROGRESSED
