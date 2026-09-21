# Release notes 0.3.67

## Resumo

Expande a fonte `BCB-OLINDA-EXPECTATIVAS` (ExpectativasMercadoAnuais) com
allowlist IPCA + Selic + Câmbio, multi-fetch por indicador e unidades
corretas. Continua distinta do SGS REST (`BCB-SGS-OLINDA`).

## Entregas

- Fonte `BCB-OLINDA-EXPECTATIVAS` (`REFERENCE_ENRICHMENT` / PUBLIC_OPEN).
- Conector `bcb_olinda_expectativas` com `max_rows=8` por indicador.
- Fixtures OData mínimas IPCA/Selic/Câmbio.
- Migration Alembic `0070_bcb_olinda_selic_cambio` → `0.3.67`.

## Não incluso

Homologação humana de Gold, carga nacional, ativação de UFs sem tabular,
merge em `main`.
