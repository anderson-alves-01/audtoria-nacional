# Plan — BCB OLINDA Expectativas PIB Agropecuária + PIB Indústria (0.3.70)

## Objetivo

Completar a decomposição setorial do PIB nas Expectativas Focus anuais
(`BCB-OLINDA-EXPECTATIVAS`, PUBLIC_OPEN) com `PIB Agropecuária` e
`PIB Indústria` (baseCalculo=1), alinhados a `PIB Total` e `PIB Serviços`.

## Escopo

- `official-catalog.yaml` — allowlist + units + layout v5
- snapshots OData + `SNAPSHOT_URLS`
- testes unit/integration (silverCount=80 = 10×8)
- migration `0073_bcb_olinda_pib_sectors` → `0.3.70`
- evidência de probe + re-probe UF
- fila / current-state / roadmap / MANIFEST

## Fora de escopo

Homologação humana, carga nacional, UFs PDF/HTML/IP-blocked,
indicadores macro com unidade distinta (Balança comercial, Dívida, etc.).
