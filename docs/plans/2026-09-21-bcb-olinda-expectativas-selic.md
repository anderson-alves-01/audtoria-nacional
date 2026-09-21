# Plan — BCB OLINDA Expectativas Selic por reunião Copom (0.3.96)

## Objetivo

Ativar nova fonte `BCB-OLINDA-EXPECTATIVAS-SELIC` (PUBLIC_OPEN) via entity set
`ExpectativasMercadoSelic` com allowlist `Selic`, `baseCalculo=1`, max_rows=8.
Horizonte = campo `Reuniao` (ex.: R1/2027), distinto de Selic anual
(`ExpectativasMercadoAnuais`) e de Selic trimestral (vazio na fonte).

## Critérios de aceite

- Source TECHNICALLY_APPROVED; connector `bcb_olinda_expectativas`
- Layout `bcb-olinda-expectativas-selic-v1`; silverCount 8
- Focus label `FOCUS_SELIC`; unidade `PERCENT_PER_YEAR`
- Fixture oficial mínima; mediana R1/2027 = 13.25
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Migration `0099_bcb_olinda_selic` → `0.3.96`
- Fora desta fatia: Inflacao12/24m e Top5; UFs restantes bloqueadas

## Rollback

Alembic → `0098_state_sc_activation`; remover source SELIC do catálogo.
