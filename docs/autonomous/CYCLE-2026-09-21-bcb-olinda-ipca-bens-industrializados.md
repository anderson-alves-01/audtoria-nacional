# Ciclo 2026-09-21 — BCB OLINDA IPCA Bens industrializados

## Resultado

`CYCLE_RESULT=PROGRESSED` — versão `0.3.79`.

## Fatia

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`IPCA Bens industrializados`
  (PERCENT_PER_YEAR, baseCalculo=1)
- Layout v14; silverCount 184 (23×8); migration `0082_bcb_olinda_ipca_bens` → `0.3.79`
- Evidência: `evidence/releases/0.3.79/`
- UF re-probe: nenhum ACTIVATE_NOW (status herdado de 0.3.78)
- Próximo candidato técnico: UF tabular nova quando publicada; ou outro
  indicador Focus OLINDA ainda fora da allowlist

## Rollback

Reverter migration para `0081_bcb_olinda_ipca_admin` e remover
`IPCA Bens industrializados` da allowlist no catálogo/runtime.
