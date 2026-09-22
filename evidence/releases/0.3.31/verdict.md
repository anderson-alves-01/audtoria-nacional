# 0.3.31 — ANP revendedores UF-scoped activation

## Verdict

TECHNICAL_GO for ANP-REVENDEDORES activation via official REST API with UF=MS
scope, minimized fixture, municipality aggregation + IBGE7 join, CNPJ dropped
from Silver/Gold. Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
No human homologation requested.

## Delivered

- Connector `anp_revendedores_api` for `ANP-REVENDEDORES`
- Endpoint `.../v1/combustivel?uf=MS&numeropagina=1`
- REFERENCE_QUANTITY Gold (establishment counts); lineage complete
- Sectoral panel `PARTIAL_TECHNICAL_ACTIVATION`; other sectorals still blocked
- Migration `0034_anp_revendedores_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — web specs

## Non-goals

- National ANP load, ANEEL/EPE/Anatel/BCB/CNES activation, UF ICMS/IPVA beyond
  prior activations, RFB national load, human Gold validation, tax credit
