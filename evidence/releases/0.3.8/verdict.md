# Verdict 0.3.8 — Alembic hygiene

## Result

`GO` for local migration hygiene. Human gates unchanged.

## Reproduction

Command: isolated `sirta_migtest`, `upgrade 0004`, `Base.metadata.drop_all`, `upgrade 0005`.

Before fix (`evidence/releases/0.3.8/repro-0004-0005.txt`):

- `alembic_version=0004_s2_validation`
- `tenants` table absent
- `IntegrityError users_tenant_id_fkey` on `collector.alpha`

## Acceptance mapped to evidence

| Criterion | Result |
|---|---|
| `base -> head` empty DB | pytest `test_upgrade_base_to_head_on_empty_database` |
| `0004 -> head` with seed | `test_upgrade_0004_to_head_with_valid_seed` |
| `0004 -> head` after domain drop_all | `test_upgrade_0004_to_head_after_domain_drop_all` |
| Seed twice | `test_seed_synthetic_is_idempotent` |
| pytest does not drop_all | `test_conftest_does_not_drop_all_on_shared_database` |
| Compose migrate | `docker compose config` exit 0; `docker compose run --rm migrate` exit 0 |
| Full pytest | 81 passed |
| Angular | 12 ChromeHeadless SUCCESS |

## Commands

- `python -m ruff format --check apps tests alembic` (exit 0)
- `python -m ruff check apps tests alembic` (exit 0)
- `python -m openapi_spec_validator contracts/openapi/sirta-v1.yaml` (exit 0)
- `python -m pytest tests -q` (81 passed)
- `npm test` in `apps/web` (12 SUCCESS)
- `docker compose config --quiet` (exit 0)
- `docker compose run --rm migrate` (exit 0)

## Rollback

`git revert` of the 0.3.8 commit. `0010` is additive.

## Human gates

G0/G1/G4/G7 official/G8 official/G9/G10 remain BLOCKED.
