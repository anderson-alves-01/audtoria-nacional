# Plan — BCB OLINDA Expectativas Taxa de desocupação (0.3.75)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` (PUBLIC_OPEN) com
`Taxa de desocupação` (`PERCENT`, baseCalculo=1 default).

## Escopo

- `official-catalog.yaml` — allowlist + units + layout v10
- snapshot OData + `SNAPSHOT_URLS`
- testes unit/integration (silverCount=136 = 17×8)
- migration `0078_bcb_olinda_taxa_desocup` → `0.3.75`
- evidência de probe + re-probe UF
- fila / current-state / roadmap / MANIFEST

## Fora de escopo

Homologação humana, carga nacional, UFs PDF/HTML/IP-blocked.
