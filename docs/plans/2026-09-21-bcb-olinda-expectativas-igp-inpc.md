# Plan — BCB OLINDA Expectativas IGP-M + IGP-DI + INPC (0.3.69)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` (PUBLIC_OPEN) para incluir índices
`IGP-M` (baseCalculo=1), `IGP-DI` e `INPC` (baseCalculo=0), com multi-fetch
por indicador e suporte a `indicator_base_calculo` no conector.

## Escopo

- `official-catalog.yaml` — allowlist + units + base map + layout v4
- `official_ingest.py` — URL com baseCalculo por indicador
- `sectoral_enrichment.py` / `gold.py` — labels
- snapshots + `SNAPSHOT_URLS`
- testes unit/integration (silverCount=64)
- migration `0072_bcb_olinda_igp_inpc` → `0.3.69`
- evidência de re-probe UF

## Fora de escopo

Homologação humana, carga nacional, UFs PDF/HTML/IP-blocked.
