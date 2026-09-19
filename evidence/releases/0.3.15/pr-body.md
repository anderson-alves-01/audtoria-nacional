## Summary

- Correct the premature `REAL_DATA_PIPELINES_COMPLETE_AWAITING_HUMAN_VALIDATION` declaration. Current state is `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS` (implementation `0.3.15`).
- Gold lines now carry lineage to Silver, Bronze SHA-256, landing manifest and official URL. Invariant tests fail on incomplete lineage, test-only runtime data, metadata-as-money, public sources creating credit, and quarantine in Gold.
- Activate Tesouro CKAN monthly CSV (`Transferencia_Mensal_Municipios_202609.csv`) for published FPM amounts, with IBGE join via SICONFI/entes. The Aria dictionary remains catalog metadata, not a transfer value.
- Enable partitioned SICONFI RREO/DCA ingest with checkpoints and `max_entes_per_run`. `SICONFI-ENTES` stays a coverage registry, not a fiscal statement.
- EC 132 uses Planalto with Senado fallback, retry/backoff, `binding=false` / `NON_BINDING`.
- Generic ICMS/IPVA adapters plus a 26+DF catalog; no unverified state source was activated. RFB CNPJ is `READY_FOR_TERRITORIAL_SCOPE` without a national or sample load. Restricted municipal connectors stay `CREDENTIAL_REQUIRED` and empty.
- Fifteen official dashboards are routed. Modules without authorized Gold stay empty. No synthetic fill. Commands that could collect, enroll or decide remain disabled.

The ROADMAP is **not** complete. Do not merge to `main`. Human validation is **not** requested in this update.

## Test plan

- [x] `python -m pytest -q` — 114 passed, 1 skipped
- [x] `npm test` in `apps/web` — 17 SUCCESS
- [x] `python -m ruff check apps/api/src/sirta_api tests`
- [x] `terraform -chdir=infra/terraform/environments/local validate` (no apply)
- [ ] CI python/web/containers green on this push
