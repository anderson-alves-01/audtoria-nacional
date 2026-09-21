# Plan — BCB OLINDA Expectativas Selic + Câmbio (0.3.67)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` (PUBLIC_OPEN) de allowlist IPCA para
`IPCA`, `Selic` e `Câmbio`, com multi-fetch por indicador (padrão SGS),
unidades corretas e fixture mínima. Sem crédito tributário.

## Escopo

- `parsers.py` — unidades por indicador (`PERCENT_PER_YEAR` / `BRL_PER_USD`)
- `official_ingest.py` — `_parse_bcb_olinda_expectativas_allowlist`
- catálogo + snapshots Selic/Câmbio + `SNAPSHOT_URLS`
- `gold.py`, `sectoral_enrichment.py`, testes unit/integration
- migration `0070_bcb_olinda_selic_cambio` → `0.3.67`
- evidência, fila, roadmap, `current-state.yaml`

## Fora de escopo

UF restantes sem tabular; carga nacional; homologação humana; merge em main.
