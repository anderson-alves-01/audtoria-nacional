# Verdict 0.3.95

## Slice

Activate Santa Catarina SEF `Anual_2017.csv` ICMS/IPVA/IPI PUBLIC_OPEN
historical quotas via `state_sc_csv`.

## Checks

- Unit: `test_state_sc_csv_joins_ibge_and_quarantines_territory`, state panel
- Integration: SC ingest gold lineage without credit; alembic head `0098`
- Migration: `0098_state_sc_activation` -> implementation_version `0.3.95`
- Probe SHA-256: `3a13beda5f1445d09b9d924ac0b9c80834718bdf21491c98b38088253903d79d` (84706 bytes)

## Constraints preserved

- No tax credit from public transfer data
- Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
- No national load; fixture-minimized only
- CKAN SC arrecadação not used as quota
