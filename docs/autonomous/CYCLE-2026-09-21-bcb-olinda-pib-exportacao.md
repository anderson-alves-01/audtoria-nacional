# Ciclo 2026-09-21 — BCB OLINDA PIB Exportação de bens e serviços

## Fatia

`PIB Exportação de bens e serviços` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Mudanças

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`PIB Exportação de bens e serviços`
- Fixture + HTTP helper + unit/integration (silverCount=216)
- Layout v18; silverCount 216 (27×8); migration `0086_bcb_olinda_pib_exportacao` → `0.3.83`
- UF re-probe: nenhum ACTIVATE_NOW

## Rollback

Reverter migration para `0085_bcb_olinda_pib_despesa_adm` e remover
`PIB Exportação de bens e serviços` da allowlist no catálogo/runtime.
