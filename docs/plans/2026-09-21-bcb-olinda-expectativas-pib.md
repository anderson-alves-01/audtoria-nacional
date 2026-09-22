# Plan — BCB OLINDA Expectativas PIB Total + PIB Serviços (0.3.68)

## Objetivo

Expandir `BCB-OLINDA-EXPECTATIVAS` (PUBLIC_OPEN) de allowlist
IPCA/Selic/Câmbio para incluir `PIB Total` e `PIB Serviços`, com
multi-fetch por indicador, unidades `PERCENT_PER_YEAR` e fixtures mínimas.

## Escopo

- `official-catalog.yaml` — allowlist + units + layout v3
- `sectoral_enrichment.py` / `gold.py` — labels
- snapshots + `SNAPSHOT_URLS`
- testes unit/integration (silverCount=40)
- migration `0071_bcb_olinda_pib` → `0.3.68`
- evidência de re-probe UF (nenhuma ACTIVATE_NOW)

## Fora de escopo

Homologação humana, carga nacional, UFs PDF/HTML/IP-blocked.
