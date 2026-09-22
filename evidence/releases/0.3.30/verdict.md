# 0.3.30 — MS ICMS/IPVA DataStore activation

## Verdict

TECHNICAL_GO for Mato Grosso do Sul state ICMS and IPVA activation via official
CKAN DataStore monthly dumps. Gold remains
`REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`. No human homologation requested.

## Delivered

- Connector `state_ms_csv` for `ESTADO-MS-ICMS-QUOTA` / `ESTADO-MS-IPVA-QUOTA`
- Official endpoint: datastore dump `repasses-dos-municipios-01_2026`
- Filter by `Tipo_Repasse`; name+UF IBGE7 join; minimized fixture; Gold lineage
- MS `TECHNICALLY_APPROVED` with `taxes: [ICMS, IPVA, ...]`; prior UFs unchanged
- Migration `0033_state_ms_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — web specs

## Non-goals

- RJ activation, GO ICMS, RFB national load, human Gold validation, tax credit
