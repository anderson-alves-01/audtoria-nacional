# Ciclo 2026-09-21 — BCB OLINDA IPCA Administrados + Alimentação

## Resultado

`CYCLE_RESULT=PROGRESSED` — versão `0.3.78`.

## Fatia

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`IPCA Administrados`,
  +`IPCA Alimentação no domicílio` (PERCENT_PER_YEAR, baseCalculo=1)
- Layout v13; silverCount 176 (22×8); migration `0081_bcb_olinda_ipca_admin` → `0.3.78`
- Evidência: `evidence/releases/0.3.78/`
- UF re-probe: nenhum ACTIVATE_NOW
- Próximo candidato técnico: `IPCA Bens industrializados` (probe OK) ou UF tabular nova

## Rollback

Reverter migration para `0080_bcb_olinda_ipca_livres` e remover os dois
indicadores da allowlist no catálogo/runtime.
