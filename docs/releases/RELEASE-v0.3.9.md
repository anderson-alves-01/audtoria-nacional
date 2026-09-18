# Release v0.3.9 - F3.0 source master registry (synthetic)

`release_stage: F3_SOURCE_CATALOG_LOCAL`  
Spec 0.3.0 unchanged.

GET `/v1/data-sources` and POST dry-run. Public sources never create tax credits. Restricted municipal ISS stays DISCOVERED without ingestion.

Rollback: `git revert`. Migration `0011` is additive.

Evidence: `evidence/releases/0.3.9/`
