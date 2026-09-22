# Plan — BCB OLINDA Expectativas Dívida bruta (0.3.74)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` (PUBLIC_OPEN) com
`Dívida bruta do governo geral` (`PERCENT_OF_GDP`, baseCalculo=0).

## Escopo

- `official-catalog.yaml` — allowlist + units + layout v9
- snapshot OData + `SNAPSHOT_URLS`
- testes unit/integration (silverCount=128 = 16×8)
- migration `0077_bcb_olinda_divida_bruta` → `0.3.74`
- evidência de probe + re-probe UF
- fila / current-state / roadmap / MANIFEST

## Fora de escopo

Homologação humana, carga nacional, UFs PDF/HTML/IP-blocked.
