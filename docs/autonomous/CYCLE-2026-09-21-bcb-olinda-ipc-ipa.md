# Ciclo 2026-09-21 — BCB OLINDA IPC-Fipe / IPA-M / IPA-DI

## Fatia

`IPC-Fipe`, `IPA-M` e `IPA-DI` (PERCENT_PER_YEAR, baseCalculo=0) via
multi-fetch `bcb_olinda_expectativas` (PUBLIC_OPEN).

## Alterações

- Allowlist `BCB-OLINDA-EXPECTATIVAS`: +`IPC-Fipe` +`IPA-M` +`IPA-DI`
- `indicator_base_calculo` =0 para os três (base=1 vazio na fonte)
- Layout `bcb-olinda-expectativas-anuais-v22`; silverCount 264
- Séries congeladas na fonte em 2021-02-17 (ainda PUBLIC_OPEN)
- Próximo OLINDA: demais Focus anuais fora da allowlist

## Rollback

Remover os três da allowlist no catálogo/runtime; Alembic → `0089_bcb_olinda_ipca15`.
