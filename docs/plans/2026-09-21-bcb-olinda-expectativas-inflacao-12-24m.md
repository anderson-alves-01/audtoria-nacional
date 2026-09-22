# Plan — BCB OLINDA Expectativas Inflação 12m/24m (0.3.97)

## Objetivo

Ativar fontes `BCB-OLINDA-EXPECTATIVAS-INFLACAO-12M` e
`BCB-OLINDA-EXPECTATIVAS-INFLACAO-24M` (PUBLIC_OPEN) via entity sets
`ExpectativasMercadoInflacao12Meses` / `ExpectativasMercadoInflacao24Meses`
com allowlist de indicadores Focus, `baseCalculo=1`, `horizon_field=Suavizada`,
max_rows=8 por indicador.

## Critérios de aceite

- Sources TECHNICALLY_APPROVED; connector `bcb_olinda_expectativas`
- Layouts `bcb-olinda-expectativas-inflacao12m-v1` e `…-inflacao24m-v1`
- Focus labels `FOCUS_INFLACAO_12M` / `FOCUS_INFLACAO_24M`; unidade `PERCENT_PER_YEAR`
- 12m allowlist: IPCA, IGP-M, IPCA Livres, IPCA Serviços → silverCount 8
- 24m allowlist: IPCA, IPCA Livres, IPCA Serviços, IPCA Bens industrializados → silverCount 8
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Migration `0100_bcb_olinda_inflacao_12_24m` → `0.3.97`
- Fora desta fatia: Top5; UFs restantes bloqueadas

## Rollback

Alembic → `0099_bcb_olinda_selic`; remover sources INFLACAO-12M/24M do catálogo.
