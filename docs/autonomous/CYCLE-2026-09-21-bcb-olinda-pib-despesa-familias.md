# Ciclo 2026-09-21 — BCB OLINDA PIB Despesa de consumo das famílias

## Fatia

`PIB Despesa de consumo das famílias` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Alterações

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`PIB Despesa de consumo das famílias`
- Fixture + HTTP helper + unit/integration (silverCount=200)
- Layout v16; silverCount 200 (25×8); migration `0084_bcb_olinda_pib_despesa_fam` → `0.3.81`
- UF re-probe: nenhum ACTIVATE_NOW (herdado 0.3.80)

## Rollback

Reverter migration para `0083_bcb_olinda_pib_fbcf` e remover
`PIB Despesa de consumo das famílias` da allowlist no catálogo/runtime.
