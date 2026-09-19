# 0.3.32 — ANEEL IndQual Município UF-scoped activation

## Verdict

TECHNICAL_GO for ANEEL-DADOS-ABERTOS activation via official CKAN DataStore
IndQual Município with UF=MS scope, minimized fixture, IBGE7-native aggregation.
Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
No human homologation requested.

## Delivered

- Connector `aneel_ckan_open` for `ANEEL-DADOS-ABERTOS`
- Endpoint datastore_search resource `3f841488-80a8-42f2-a6ca-e0c593b228de` UF=MS limit=8
- REFERENCE_QUANTITY Gold (consumer unit set counts); lineage complete
- Sectoral panel `PARTIAL_TECHNICAL_ACTIVATION` (ANP+ANEEL); other sectorals blocked
- Migration `0035_aneel_indqual_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — web specs

## Non-goals

- National ANEEL load, EPE/Anatel/BCB/CNES activation, UF ICMS/IPVA beyond
  prior activations, RFB national load, human Gold validation, tax credit
