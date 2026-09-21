# Plan — BCB OLINDA Expectativas IPC-Fipe / IPA-M / IPA-DI (0.3.87)

## Objetivo

Ativar indicadores Focus anuais `IPC-Fipe`, `IPA-M` e `IPA-DI`
(PERCENT_PER_YEAR, baseCalculo=0) no conector multi-fetch
`bcb_olinda_expectativas`.

Nota: séries oficiais com última publicação em 2021-02-17; ainda PUBLIC_OPEN
e fetcháveis. Documentar staleness na evidência; não inventar dados recentes.
baseCalculo=1 retorna zero linhas na fonte; override obrigatório =0.

## Critérios de aceite

- allowlist + units + `indicator_base_calculo` =0 para os três no catálogo
- fixtures OData mínimas (8 linhas cada)
- HTTP helper mapeia URLs com baseCalculo=0
- unit parse Medianas 3.88 / 8.76 / 8.87; silverCount integração=264 (33×8)
- layout `bcb-olinda-expectativas-anuais-v22`
- migration `0090_bcb_olinda_ipc_ipa` → `0.3.87`
- Gold REFERENCE_QUANTITY; sem crédito
- próximo OLINDA: demais indicadores Focus anuais ainda fora da allowlist

## Rollback

Downgrade Alembic para `0089_bcb_olinda_ipca15` e remover os três indicadores
da allowlist no catálogo/runtime.
