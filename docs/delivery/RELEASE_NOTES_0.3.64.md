# RELEASE NOTES 0.3.64

## Resumo

Ativação do CSV COINT `LC 87/96 por Município` do Tesouro Transparente
(`TESOURO-LC87-VALORES`), reutilizando o conector
`tesouro_coint_municipio_csv`.

## Entrega

- Série histórica oficial (valores não nulos até 2018; colunas 2019–2020
  publicadas vazias). Competência técnica `2018-01`.
- Distinto de `TESOURO-LC176-VALORES` (CSV mensal constitucional).
- Fixture mínima latin-1; `max_rows=8`.
- Dashboard `/transferencias` inclui a nova fonte.
- Migration Alembic `0067_tesouro_lc87_coint` →
  `implementation_version=0.3.64`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- UFs restantes sem tabular recente: RJ (IP block), PI ICMS, SP, SC≤2017,
  RR, PA plena, AP, MT, SE/PB, AM, TO.
