# Verdict 0.3.61

## Fatia

RS Compensação LC 194/22 via SEFAZ-RS MontaArquivo
(`l_compensacao_perdas_icms_2024`, aba OUTUBRO 2024, coluna REPASSE*).

## Evidência

- Unit + integration: 66 passed (`evidence/releases/0.3.61/tests.txt`)
- Fonte: PUBLIC_OPEN; fixture mínima; sem crédito
- Modalidade: `COMPENSACAO_LC194_QUOTA`
- Migration: `0064_state_rs_compensacao_lc194` → implementation_version `0.3.61`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0063_ac_tr_icms_fundeb` e remover a fonte
`ESTADO-RS-COMPENSACAO-LC194-QUOTA` do catálogo/runtime.
