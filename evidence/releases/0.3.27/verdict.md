# 0.3.27 — MG ICMS/IPVA activation

## Verdict

TECHNICAL_GO for Minas Gerais state transfer CSV.gz activation. Gold remains
`REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`. No human homologation requested.

## Delivered

- Connector `state_mg_csv` for `ESTADO-MG-ICMS-QUOTA` / `ESTADO-MG-IPVA-QUOTA`
- Frictionless fact `ft_repasse_mun.csv.gz` + `dm_municipio` + `dm_tempo_mensal`
- Native IBGE7; territories without 7-digit IBGE quarantined
- Fixture minimized (Abadia dos Dourados, Belo Horizonte, one territory)
- MG `TECHNICALLY_APPROVED` with `ingest_allowed=true`; PE/BA unchanged; RJ IP-blocked
- Migration `0030_state_mg_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — web specs (44 SUCCESS)

## Non-goals

- RJ activation, RFB national load, human Gold validation, tax credit
