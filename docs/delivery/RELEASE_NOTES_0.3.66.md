# RELEASE NOTES 0.3.66

## Fatia

Ativação da API OLINDA Expectativas Focus anuais do Banco Central
(`ExpectativasMercadoAnuais`) com allowlist IPCA, distinta do SGS REST
já ativado em `BCB-SGS-OLINDA`.

## Entregas

- Fonte `BCB-OLINDA-EXPECTATIVAS` (`REFERENCE_ENRICHMENT` / PUBLIC_OPEN).
- Conector `bcb_olinda_expectativas` com `max_rows=8` e fixture OData mínima.
- Painel setorial e dashboard `/economia` incluem a fonte.
- Migration Alembic `0069_bcb_olinda_expectativas` →
  `implementation_version=0.3.66`.

## Restrições

- Allowlist apenas IPCA; sem scrape; sem crédito.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
