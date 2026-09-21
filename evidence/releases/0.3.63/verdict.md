# Verdict 0.3.63

## Fatia

Tesouro COINT FUNDEB por município (`TESOURO-FUNDEB-VALORES`) via conector
`tesouro_coint_municipio_csv` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt`
- Fonte: PUBLIC_OPEN; fixture mínima latin-1; sem crédito
- Modalidade: `FUNDEB_RECEIVED`
- Distinto de complementação COUN/AJUSTE e retenções FPM→FUNDEB
- Migration: `0066_tesouro_fundeb_coint` → implementation_version `0.3.63`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0065_tesouro_fundeb_complement` e remover a fonte
`TESOURO-FUNDEB-VALORES` do catálogo/runtime.
