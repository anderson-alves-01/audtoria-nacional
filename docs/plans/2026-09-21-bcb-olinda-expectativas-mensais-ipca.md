# Plan — BCB OLINDA Expectativas mensais IPCA (0.3.89)

## Objetivo

Ativar entity set Focus `ExpectativaMercadoMensais` como fonte
`BCB-OLINDA-EXPECTATIVAS-MENSAIS` (PUBLIC_OPEN), allowlist inicial `IPCA`
(baseCalculo=1, max_rows=8).

## Critérios de aceite

- Conector `bcb_olinda_expectativas` respeita `parameters.entity_set`
- Parser usa rótulo `FOCUS_MENSAL` e unidade `PERCENT_PER_MONTH`
- Catálogo + Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Fixture OData mínima (8 linhas); Mediana prova 0.4937 (Data 2026-09-18)
- Integração: silverCount=8; lineage Gold
- Migration `0092_bcb_olinda_mensais_ipca` → `0.3.89`
- Próximo: demais indicadores mensais ativos (IGP-M, Câmbio, IPCA Livres…)
  ou entity set trimestral

## Rollback

Remover fonte mensal do catálogo; Alembic → `0091_bcb_olinda_balanca_exim`.
