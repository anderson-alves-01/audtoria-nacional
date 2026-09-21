# RELEASE NOTES 0.3.61

## Resumo

Ativação da Compensação de perdas de ICMS LC 194/22 no Rio Grande do Sul a
partir do XLS PUBLIC_OPEN SEFAZ-RS MontaArquivo
(`l_compensacao_perdas_icms_2024`, aba OUTUBRO 2024, coluna `REPASSE*`).

## Entrega

- Parser `state_rs_xls` aceita `tax=COMPENSACAO_LC194` além de ICMS/IPVA.
- Fonte `ESTADO-RS-COMPENSACAO-LC194-QUOTA`.
- Dashboard `/transferencias` inclui a nova fonte.
- Migration Alembic `0064_state_rs_compensacao_lc194` —
  `implementation_version=0.3.61`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- Modalidade `COMPENSACAO_LC194_QUOTA` (ocorrência, não crédito).
- UFs restantes sem tabular recente: RJ, PI ICMS, SP, SC≤2017, RR, PA plena,
  AP, MT, SE/PB, AM, TO.
