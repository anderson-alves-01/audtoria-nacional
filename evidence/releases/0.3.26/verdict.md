# 0.3.26 — BA ICMS/IPVA activation

## Verdict

TECHNICAL_GO for Bahia state transfer CSV activation. Gold remains
`REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`. No human homologation requested.

## Delivered

- Connector `state_ba_csv` for `ESTADO-BA-ICMS-QUOTA` / `ESTADO-BA-IPVA-QUOTA`
- Multi-header semicolon CSV parser (utf-8/latin-1, Brazilian numbers, ICMS col 4 / IPVA col 13)
- Fixture `ba-repasses-municipios-2024.csv` + SICONFI-ENTES BA municipalities
- BA `TECHNICALLY_APPROVED` with `ingest_allowed=true`; PE unchanged; MG/RJ blocked
- Migration `0029_state_ba_activation`

## Evidence

- `tests.txt` — unit + integration
- `angular.txt` — state-transfers / app / health specs

## Non-goals

- MG/RJ activation, RFB national load, human Gold validation, tax credit
