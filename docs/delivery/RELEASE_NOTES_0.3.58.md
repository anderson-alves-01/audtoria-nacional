# RELEASE NOTES 0.3.58

## Resumo

Ativação de royalties estaduais em AL e PR nos arquivos PUBLIC_OPEN já
aprovados para ICMS/IPVA/IPI (coluna Royalties Total no XLS de AL; coluna
Royalties Petróleo no HTML SEFA/PR).

## Entrega

- Parser `state_al_xls` aceita `tax=ROYALTY` via coluna Royalties Total YYYY.
- Parser `state_pr_html` aceita `tax=ROYALTY` via coluna Royalties (índice 5).
- Fontes `ESTADO-AL-ROYALTY-QUOTA` e `ESTADO-PR-ROYALTY-QUOTA`.
- Dashboard `/transferencias` inclui as novas fontes.
- Migration Alembic `0061_state_al_pr_royalty` — `implementation_version=0.3.58`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- Modalidade publicada como `ROYALTY_QUOTA` (ocorrência, não crédito).
- UFs restantes sem tabular recente: RJ, PI ICMS, SP, SC≤2017, RR, PA plena, AP, MT, SE/PB, AM, TO.
