# RELEASE NOTES 0.3.57

## Resumo

Ativação de IPI-Exportação/FPEX estadual em MA e PR nos arquivos PUBLIC_OPEN já
aprovados para ICMS/IPVA, e de IPI-Exportação + CIDE em MS no DataStore já
aprovado (Tipo_Repasse confirmado no dump 01/2026).

## Entrega

- Parser `state_ma_xls` aceita `tax=IPI` via aba FPEX; fixture mínima inclui FPEX 1º Semestre.
- Parser `state_pr_html` aceita `tax=IPI` via coluna Fundo de Exportação (índice 4).
- Parser `state_ms_csv` aceita `tax=IPI` (`REPASSE DE IPI EXPORTAÇÃO`) e `tax=CIDE`
  (`REPASSE DA CIDE`); fixture mínima ampliada.
- Fontes `ESTADO-MA-IPI-QUOTA`, `ESTADO-PR-IPI-QUOTA`, `ESTADO-MS-IPI-QUOTA`,
  `ESTADO-MS-CIDE-QUOTA`.
- Dashboard `/transferencias` inclui as novas fontes.
- Migration Alembic `0060_state_ma_pr_ipi_fpex` — `implementation_version=0.3.57`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- Modalidade MA/PR/MS IPI publicada como IPI-Exportação/FPEX (não IPI quota clássica genérica).
- UFs restantes sem tabular recente: RJ, PI ICMS, SP, SC≤2017, RR, PA plena, AP, MT, SE/PB, AM, TO.
