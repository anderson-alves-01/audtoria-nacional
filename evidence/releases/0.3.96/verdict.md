# Verdict 0.3.96

## Slice

Activate BCB OLINDA ExpectativasMercadoSelic (FOCUS_SELIC / Reuniao) PUBLIC_OPEN.

## Checks

- Unit: `test_bcb_olinda_expectativas_parses_selic_reuniao`, sectoral panel count 10
- Integration: Selic ingest gold lineage without credit; alembic head `0099`
- Migration: `0099_bcb_olinda_selic` -> implementation_version `0.3.96`
- Probe SHA-256: `6C015279D5D30E1D605379A766F485474587FF6527A09BA93D0D44D677CDD805` (1085 bytes)
- Median sample: R1/2027 = 13.25 (Data 2026-09-18)

## Constraints preserved

- No tax credit from public enrichment data
- Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
- No national load; fixture-minimized only
- Distinct from annual Selic and empty trimestral Selic
