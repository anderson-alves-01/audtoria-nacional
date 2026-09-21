# RELEASE NOTES 0.3.60

## Resumo

Ativação de ICMS mensal e FUNDEB no Acre a partir do JSON PUBLIC_OPEN já
aprovado da Transparência AC (`state_ac_transparencia_json` colunas
`valor_icms` e `valor_fundeb`), distintos do CSV anual SEPLAG.

## Entrega

- Parser `state_ac_transparencia_json` aceita `tax=ICMS`, `tax=IPVA` e
  `tax=FUNDEB`.
- Fontes `ESTADO-AC-ICMS-TRANSPARENCIA-QUOTA` e
  `ESTADO-AC-FUNDEB-TRANSPARENCIA-QUOTA`.
- Dashboard `/transferencias` inclui as novas fontes.
- Migration Alembic `0063_ac_tr_icms_fundeb` —
  `implementation_version=0.3.60`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- Modalidades `ICMS_QUOTA` e `FUNDEB_QUOTA` (ocorrência, não crédito).
- UFs restantes sem tabular recente: RJ, PI ICMS, SP, SC≤2017, RR, PA plena, AP, MT, SE/PB, AM, TO.
