# Verdict 0.3.7 — G8 IBS/CBS local

## Result

`GO_WITH_RISK` for the **local synthetic calendar only**. Official G8 homologation remains `NO-GO`.

## Acceptance mapped to evidence

| Criterion | Evidence |
|---|---|
| Catalog items `binding=false` and `status=NON_BINDING` | `pytest.txt` (`test_ibs_cbs_calendar_is_non_binding_and_idempotent`) |
| Response `operational=false` and `homologated=false` | same |
| Operational use without homologation fails | `test_regulatory.py` |
| GET idempotent | same integration test |
| UI does not claim homologation | Angular `calendar-page.component.spec.ts` (12 tests total) |
| Spec 0.3.0 unchanged | `contracts/openapi/sirta-v1.yaml` info.version |
| OpenAPI valid | `openapi-lint.txt` |
| Lint | `ruff.txt` / `ruff-format.txt` |
| Additive migration | `0009_g8_regulatory.py`, `alembic-upgrade.txt` |

## Commands

- `python -m ruff format --check apps tests alembic`
- `python -m ruff check apps tests alembic`
- `python -m openapi_spec_validator contracts/openapi/sirta-v1.yaml`
- `python -m pytest tests -q` (75 passed)
- `cd apps/web; npm test` (12 passed)
- CI `alembic upgrade head` on empty Postgres (local host schema was dirty after pytest `drop_all`; not used as GO evidence)

## Risks accepted (non-blocking for local slice)

- Official dates, rates and layouts are not encoded as operational rules.
- G0/G1/G4/G8-official/G9/G10 remain human gates.

## Rollback

`git revert` of this commit. Table `regulatory_items` is additive.

## Implementer cannot approve

Municipal/legal homologation of IBS/CBS rules.
