# Cycle — SC SEF Anual_2017 ICMS/IPVA/IPI (0.3.95)

## Selected item

F3-STATE-ICMS-ACTIVATION / F3-STATE-IPVA-ACTIVATION — remaining UF tabular
PUBLIC_OPEN: Santa Catarina historical annual CSV.

## Why SC

- Official SEF endpoint downloads bytes (SHA-256 verified in probe).
- Precedent: AL/AC historical tabular while current is PDF/non-tabular.
- Schema: TOTAL ICMS / IPI / IPVA per municipality; join IBGE7 by name+UF.

## Evidence

- Probe: `evidence/releases/0.3.95-probe/Anual_2017.csv`
- Fixture: `tests/fixtures/official-snapshots/sc-anual-2017.csv`
- Release: `evidence/releases/0.3.95/`

## Not activated

RJ IP-blocked; PI ICMS empty; SP HTML-per-muni; MT ≤2015; SE/PB PDF;
AM HTML; AP 404; RR no split; TO IPM PDF.
