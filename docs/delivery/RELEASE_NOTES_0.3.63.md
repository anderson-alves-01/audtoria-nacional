# RELEASE NOTES 0.3.63

## Resumo

Ativação do CSV COINT `FUNDEB por município` do Tesouro Transparente
(`TESOURO-FUNDEB-VALORES`), reutilizando o conector
`tesouro_coint_municipio_csv`.

## Entrega

- Fonte distinta de `TESOURO-FUNDEB-COMPLEMENT-VALORES` (COUN/AJUSTE no CSV
  mensal) e das retenções FPM/IPI-EXP→FUNDEB.
- Fixture mínima latin-1; competência `2025-01`; `max_rows=8`.
- Dashboard `/transferencias` inclui a nova fonte.
- Migration Alembic `0066_tesouro_fundeb_coint` →
  `implementation_version=0.3.63`.

## Restrições

- Sem crédito, cobrança, inscrição ou notificação.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados.
- UFs restantes sem tabular recente: RJ (IP block), PI ICMS, SP, SC≤2017,
  RR, PA plena, AP, MT, SE/PB, AM, TO.
- LC 87/96 COINT série congelada ≤2018; não ativada nesta fatia.
