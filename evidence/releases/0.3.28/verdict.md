# 0.3.28 — ES ICMS/IPVA activation

## Verdict

TECHNICAL_GO for Espírito Santo state transfer CSV activation. Gold remains
`REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`. No human homologation requested.

## Delivered

- Connector `state_es_csv` for `ESTADO-ES-ICMS-QUOTA` / `ESTADO-ES-IPVA-QUOTA`
- Official CSV `TransfEstadoMunicipios-2024` with native IBGE7 (`CodMunicipio`)
- ICMS via `IcmsTotal`; IPVA via `Ipva`; invalid IBGE quarantined
- Fixture minimized (Afonso Cláudio, Vitória, one territory)
- ES `TECHNICALLY_APPROVED` with `ingest_allowed=true`; PE/BA/MG unchanged
- GO remains DISCOVERED (CSV download HTTP 500); RJ IP-blocked
- Migration `0031_state_es_activation`

## Evidence

- `tests.txt` — unit + integration (28 passed)
- `angular.txt` — web specs

## Non-goals

- GO/RJ activation, RFB national load, human Gold validation, tax credit
