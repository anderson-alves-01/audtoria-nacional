GO for 0.3.11 local F3.1 (IBGE synthetic catalog ingest).

- 95 pytest passed including `test_source_ingest` and Alembic head `0013_source_ingest`.
- 14 Angular tests SUCCESS.
- OpenAPI valid.
- Ingest is tech_admin-only; analyst reads Gold enrichment; RESTRICTED source returns 403.
- Fixture is synthetic; `taxCreditCreated=false`; `wouldDownloadFullBase=false`.
- Logical rollback unpublishes `gold_enrichments`.
- Human gates G0/G1/G4/G7-official/G8-official/G9/G10 remain BLOCKED.
