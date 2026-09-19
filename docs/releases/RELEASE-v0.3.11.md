# Release v0.3.11 - catalog-driven synthetic IBGE ingest

POST `/v1/data-sources/{sourceId}/ingest` promotes the synthetic IBGE/SIDRA fixture through landing, silver/quarantine and Gold enrichment. Replay is idempotent. `taxCreditCreated` remains false. Restricted municipal ISS ingest stays 403. No full SIDRA download.

Spec 0.3.0 unchanged. Rollback: `POST /v1/data-loads/{runId}/rollback` unpublishes enrichment Gold; `git revert`. Migration `0013` additive.
