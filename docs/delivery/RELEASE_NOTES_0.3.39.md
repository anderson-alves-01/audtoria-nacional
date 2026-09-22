# Release notes 0.3.39

## Fatia

Ativação técnica de ICMS e IPVA do Ceará a partir do XLS mensal oficial da SEFAZ-CE (Portaria de distribuição das cotas-partes).

## Entregas

- Connector `state_ce_xls` (coluna Total; join IBGE7 por nome+UF; competência `2025-01`)
- Fontes `ESTADO-CE-ICMS-QUOTA` e `ESTADO-CE-IPVA-QUOTA` `TECHNICALLY_APPROVED`
- Dependência `xlrd` para leitura de `.xls` legado
- Fixture mínima oficial; sem crédito; Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Não inclui

- SP (portal HTML por município; sem CSV/API verificado)
- RS (links `MontaArquivo` pendentes de layout estável nesta fatia)
- Homologação humana de Gold
- Carga nacional ou deploy
