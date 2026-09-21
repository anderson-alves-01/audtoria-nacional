# Release notes 0.3.95

## Summary

Activate Santa Catarina (SC) municipal ICMS/IPVA/IPI quota-parte from the
official SEF `Anual_2017.csv` PUBLIC_OPEN download (historical series ≤2017),
with IBGE7 join by name+UF, Gold lineage and no tax credit.

## Technical

- Connector `state_sc_csv` (`;`, latin-1, Brazilian numbers)
- Columns: TOTAL ICMS=7, IPI=9, IPVA=10
- Sources: `ESTADO-SC-ICMS-QUOTA`, `ESTADO-SC-IPVA-QUOTA`, `ESTADO-SC-IPI-QUOTA`
- Competence: `2017` (annual)
- Fixture: `tests/fixtures/official-snapshots/sc-anual-2017.csv`
- Migration: `0098_state_sc_activation` → `0.3.95`

## Out of scope

- Current SC repasse (BB portal outside `*.sc.gov.br`)
- CKAN `icms_ipva.csv` arrecadação (not quota)
- Other remaining UFs (RJ/SP/MT/SE/PB/AM/AP/RR/TO/PI ICMS)
