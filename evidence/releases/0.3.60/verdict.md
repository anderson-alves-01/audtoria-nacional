# Verdict 0.3.60

## Slice

Activate AC monthly ICMS (`valor_icms`) and FUNDEB (`valor_fundeb`) from the
already-approved PUBLIC_OPEN Transparência JSON (`state_ac_transparencia_json`),
distinct from annual SEPLAG `ESTADO-AC-ICMS-QUOTA`.

## Evidence

- Unit + integration: 65 passed (`evidence/releases/0.3.60/tests.txt`)
- Ruff format/check: green
- Sources: `ESTADO-AC-ICMS-TRANSPARENCIA-QUOTA`, `ESTADO-AC-FUNDEB-TRANSPARENCIA-QUOTA`
- Migration: `0063_ac_tr_icms_fundeb` → implementation_version `0.3.60`
- Gold remains `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
- No tax credit, collection, inscription or notification

## Next

Prefer remaining UF with recent tabular CSV/API. Blocked UFs unchanged
(RJ/PI ICMS/SP/SC/RR/PA plena/AP/MT/SE/PB/AM/TO).
