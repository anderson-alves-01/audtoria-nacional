# Release notes 0.3.41

## Fatia

Ativação técnica PUBLIC_OPEN de quotas ICMS/IPVA de Alagoas a partir do XLS anual
`repasses_estaduais.xls` em dados.al.gov.br.

## Entregue

- Connector `state_al_xls` (colunas ICMS/IPVA Total por ano; IBGE7 nativo em Código; competência `2021`)
- Fontes `ESTADO-AL-ICMS-QUOTA` e `ESTADO-AL-IPVA-QUOTA` `TECHNICALLY_APPROVED`
- Catálogo estadual AL atualizado; série corrente SEFAZ-AL permanece PDF semanal
- Fixture mínima, testes unitários/integração, lineage Gold, dashboard transferências
- Migration `0044_state_al_activation`
- Sem crédito tributário; Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Fora de escopo

- Carga nacional ilimitada
- Homologação humana de Gold
- Scraping de PDFs semanais SEFAZ-AL
- Agregadores privados
