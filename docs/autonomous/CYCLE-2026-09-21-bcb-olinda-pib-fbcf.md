# Ciclo 2026-09-21 — BCB OLINDA PIB Formação Bruta de Capital Fixo

## Fatia

`PIB Formação Bruta de Capital Fixo` (PERCENT_PER_YEAR, baseCalculo=1) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Entregas

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`PIB Formação Bruta de Capital Fixo`
  (PERCENT_PER_YEAR, baseCalculo=1)
- Layout v15; silverCount 192 (24×8); migration `0083_bcb_olinda_pib_fbcf` → `0.3.80`
- Fixture OData mínima + HTTP helper; testes unit/integration
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de 0.3.79)

## Rollback

Reverter migration para `0082_bcb_olinda_ipca_bens` e remover
`PIB Formação Bruta de Capital Fixo` da allowlist no catálogo/runtime.
