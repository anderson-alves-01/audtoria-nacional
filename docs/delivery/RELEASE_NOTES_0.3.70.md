# Release notes 0.3.70

## Fatia

BCB OLINDA Expectativas Focus anuais expandido com PIB Agropecuária e
PIB Indústria (decomposição setorial completa junto a PIB Total/Serviços).

## Entregas

- Allowlist: IPCA + Selic + Câmbio + PIB Total + PIB Serviços +
  PIB Agropecuária + PIB Indústria + IGP-M + IGP-DI + INPC.
- Conector `bcb_olinda_expectativas` com `max_rows=8` por indicador.
- Fixtures OData mínimas PIB Agropecuária/Indústria.
- Migration Alembic `0073_bcb_olinda_pib_sectors` → `0.3.70`.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Sem crédito tributário.
