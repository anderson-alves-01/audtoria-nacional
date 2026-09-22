# Plan — BCB OLINDA Expectativas Resultado primário + Conta corrente (0.3.72)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` (PUBLIC_OPEN) com `Resultado primário`
(`PERCENT_OF_GDP`, baseCalculo=1) e `Conta corrente` (`USD_BILLION`,
baseCalculo=1).

## Escopo

- `official-catalog.yaml` — allowlist + units + layout v7
- snapshots OData + `SNAPSHOT_URLS`
- testes unit/integration (silverCount=112 = 14×8)
- migration `0075_bcb_olinda_resultado_conta` → `0.3.72`
- evidência de probe + re-probe UF
- fila / current-state / roadmap / MANIFEST

## Fora de escopo

Homologação humana, carga nacional, UFs PDF/HTML/IP-blocked,
Resultado nominal (disponível na API, não priorizado nesta fatia).
