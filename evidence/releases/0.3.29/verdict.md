# 0.3.29 — GO IPVA DataStore activation

## Verdict

TECHNICAL_GO for Goiás state IPVA activation via official CKAN DataStore dump.
Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`. No human homologation
requested.

## Delivered

- Connector `state_go_csv` for `ESTADO-GO-IPVA-QUOTA`
- Official endpoint: datastore dump (CSV resource upload still HTTP 500)
- Published 2026 monthly schema has IPVA only (`VALR_IPVA`); ICMS not activated
- Name+UF IBGE7 join; minimized fixture; Gold lineage
- GO `TECHNICALLY_APPROVED` with `taxes: [IPVA]`; PE/BA/MG/ES unchanged
- Migration `0032_state_go_ipva_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — web specs

## Non-goals

- GO ICMS, RJ activation, RFB national load, human Gold validation, tax credit
