# Ciclo 2026-09-21 — Tesouro LC 87/96 COINT

## Seleção

Única fonte COINT do dataset Transferências Obrigatórias ainda sem
ativação: `LC 87/96 por Município` (resource
`06aed495-8f46-4852-97f1-ae49822aa179`).

## Implementação

- Fonte `TESOURO-LC87-VALORES` no catálogo oficial.
- Conector `tesouro_coint_municipio_csv` com `transfer_name=LC 87/96`,
  competência `2018-01`, `max_rows=8`.
- Fixture mínima + testes unitário/integração.
- Migration `0067_tesouro_lc87_coint` → `0.3.64`.
- Dashboard `/transferencias` inclui a fonte.

## Notas

Série histórica: valores não nulos até 2018; colunas 2019–2020 vazias no
probe. Distinto de LC176 mensal. Sem crédito. Sem carga nacional.
