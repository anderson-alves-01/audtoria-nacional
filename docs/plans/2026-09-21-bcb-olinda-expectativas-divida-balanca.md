# Plan — BCB OLINDA Expectativas Dívida + Balança Saldo (0.3.71)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` (PUBLIC_OPEN) com indicadores de unidade
distinta: `Dívida líquida do setor público` (`PERCENT_OF_GDP`, baseCalculo=0)
e `Balança comercial` filtrado por `IndicadorDetalhe=Saldo` (`USD_BILLION`).

## Escopo

- `official-catalog.yaml` — allowlist + units + `indicator_detalhe` + layout v6
- URL builder com suporte a `IndicadorDetalhe`
- snapshots OData + `SNAPSHOT_URLS`
- testes unit/integration (silverCount=96 = 12×8)
- migration `0074_bcb_olinda_divida_balanca` → `0.3.71`
- evidência de probe + re-probe UF
- fila / current-state / roadmap / MANIFEST

## Fora de escopo

Homologação humana, carga nacional, UFs PDF/HTML/IP-blocked,
Exportações/Importações da Balança (só Saldo nesta fatia).
