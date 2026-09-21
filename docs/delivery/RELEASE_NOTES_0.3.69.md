# Release notes 0.3.69

## Fatia

BCB OLINDA Expectativas Focus anuais expandido com IGP-M, IGP-DI e INPC.
Conector passa a respeitar `indicator_base_calculo` (IGP-DI/INPC = 0).

## Entregas

- Allowlist: IPCA + Selic + Câmbio + PIB Total + PIB Serviços + IGP-M + IGP-DI + INPC.
- Conector `bcb_olinda_expectativas` com `max_rows=8` por indicador e base por indicador.
- Fixtures OData mínimas IGP-M/IGP-DI/INPC.
- Migration Alembic `0072_bcb_olinda_igp_inpc` → `0.3.69`.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Sem crédito tributário.
