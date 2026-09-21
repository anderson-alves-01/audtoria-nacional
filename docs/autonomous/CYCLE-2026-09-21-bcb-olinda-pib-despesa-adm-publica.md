# Ciclo 2026-09-21 — BCB OLINDA PIB Despesa de consumo da administração pública

## Fatia

`PIB Despesa de consumo da administração pública` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Mudanças

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`PIB Despesa de consumo da administração pública`
- Fixture + HTTP helper + unit/integration (silverCount=208)
- Layout v17; silverCount 208 (26×8); migration `0085_bcb_olinda_pib_despesa_adm` → `0.3.82`
- UF re-probe: nenhum ACTIVATE_NOW

## Rollback

Reverter migration para `0084_bcb_olinda_pib_despesa_fam` e remover
`PIB Despesa de consumo da administração pública` da allowlist no catálogo/runtime.
