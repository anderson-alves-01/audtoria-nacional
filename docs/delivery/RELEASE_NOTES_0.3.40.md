# Release notes 0.3.40

## Fatia

Ativação técnica de ICMS e IPVA do Rio Grande do Sul a partir dos XLS mensais oficiais SEFAZ-RS (`MontaArquivo`).

## Entregas

- Connector `state_rs_xls` (ICMS coluna TOTAL MÊS/ANO REPASSE; IPVA coluna Total Mês; join IBGE7 por nome+UF; competência `2025-01`)
- Fontes `ESTADO-RS-ICMS-QUOTA` e `ESTADO-RS-IPVA-QUOTA` `TECHNICALLY_APPROVED`
- Endpoints estáveis `l_icms_rep_YYYYMM` / `l_ipva_rep_YYYYMM`
- Fixture mínima oficial; sem crédito; Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Não inclui

- SP (portal HTML por município; sem CSV/API verificado)
- Homologação humana de Gold
- Carga nacional ou deploy
