# Release notes 0.3.68

## Resumo

Expande a fonte `BCB-OLINDA-EXPECTATIVAS` (ExpectativasMercadoAnuais) com
allowlist IPCA + Selic + Câmbio + PIB Total + PIB Serviços. Continua
distinta do SGS REST (`BCB-SGS-OLINDA`).

## Entregas

- Fonte `BCB-OLINDA-EXPECTATIVAS` (`REFERENCE_ENRICHMENT` / PUBLIC_OPEN).
- Conector `bcb_olinda_expectativas` com `max_rows=8` por indicador.
- Fixtures OData mínimas PIB Total/PIB Serviços.
- Migration Alembic `0071_bcb_olinda_pib` → `0.3.68`.
- Re-probe 2026-09-21 das UFs restantes: nenhuma tabular recente ativável.

## Não incluso

Homologação humana de Gold, carga nacional, ativação de UFs sem tabular,
merge em `main`.
