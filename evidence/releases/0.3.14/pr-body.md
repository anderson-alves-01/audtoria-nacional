## Summary
- Replace synthetic dashboard data with cataloged PUBLIC_OPEN extracts from IBGE/SIDRA, SICONFI/entes and the Tesouro constitutional transfer dictionary.
- Persist Landing/Bronze checksums, Silver quarantine and Gold with REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION; never HOMOLOGATED.
- Keep restricted ISS, FPM municipal values, state ICMS quota, RFB national open data and Planalto live fetch inactive or empty instead of inventing substitutes.

## Test plan
- [x] python -m pytest tests -q (106 passed, 1 skipped live)
- [x] npm test in apps/web (16 SUCCESS)
- [x] Live ingest of IBGE 6579/5938, SICONFI entes and Tesouro dictionary; manifests in evidence/official-ingest/2026-09-19/
- [ ] CI python/web/containers green
- [ ] Human validation package docs/delivery/HUMAN_VALIDATION_PACKAGE.md
