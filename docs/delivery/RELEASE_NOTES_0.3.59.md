# RELEASE NOTES 0.3.59

## Resumo

Ativação de Fundo de Redução das Desigualdades (FRD) e Compensação Financeira
estaduais no Espírito Santo, nas colunas já publicadas do CSV PUBLIC_OPEN
TransfEstadoMunicipios-2024.

## Entrega

- Parser `state_es_csv` aceita `tax=FRD` (`FundoReducaoDesigualdades`) e
  `tax=COMPENSACAO` (`CompensacaoFinanceira`).
- Fontes `ESTADO-ES-FRD-QUOTA` e `ESTADO-ES-COMPENSACAO-QUOTA`.
- Dashboard `/transferencias` inclui as novas fontes.
- Migration Alembic `0062_state_es_frd_compensacao` — `implementation_version=0.3.59`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- Modalidades `FRD_QUOTA` e `COMPENSACAO_QUOTA` (ocorrência, não crédito).
- UFs restantes sem tabular recente: RJ, PI ICMS, SP, SC≤2017, RR, PA plena, AP, MT, SE/PB, AM, TO.
