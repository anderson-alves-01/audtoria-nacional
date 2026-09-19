# 0.3.25 — PE ICMS/IPVA activation

## Verdict

GO_LOCAL for PE state transfer CSV activation. Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`. Human gates unchanged.

## Scope

- Connector `state_pe_csv` for `ESTADO-ICMS-QUOTA` / `ESTADO-IPVA-QUOTA`
- Fixture `pe-transferencias-municipais-2024.csv` (minimized official snapshot)
- IBGE7 join by municipality name + UF via SICONFI-ENTES lookup
- Zero IPVA published as official value
- BA/MG/RJ without ingest; RFB still territorial-gated
- Migration `0028_state_pe_activation`

## Evidence

- Python targeted: see `tests.txt`
- Angular: 44 SUCCESS (`angular.txt`)
- No tax credit created from public state transfers
