# 0.3.24 — RFB territorial + state ICMS/IPVA provenance

## Verdict

PROGRESSED. RFB connector technical capabilities complete without national load.
RJ state CSV provenance verified in catalog; ingest not activated (SEFAZ IP filter).

## Tests

- Python targeted: 22 passed (`evidence/releases/0.3.24/tests.txt`)
- Angular: 6 SUCCESS (`evidence/releases/0.3.24/angular.txt`)

## Rollback

`alembic downgrade 0026_controlled_backfill`

## Not done

State ingest activation, RFB scoped runtime load, human Gold validation.
