# Release v0.3.12 - Tesouro synthetic stub and blocked G0/G1 checklists

Catalog ingest accepts `TESOURO-TRANSPARENTE` from a synthetic fixture. GET `/v1/program-gates` now includes unmet G0/G1 checklists and `canApprove=false`. Angular `/gates` is read-only.

Spec 0.3.0 unchanged. Rollback: `git revert`. Migration `0014` additive. Official Tesouro connectors remain blocked.
