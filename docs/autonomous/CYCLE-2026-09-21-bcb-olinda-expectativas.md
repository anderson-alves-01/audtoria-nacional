# Ciclo 2026-09-21 — BCB OLINDA Expectativas Focus (IPCA)

## Seleção

UFs restantes sem tabular estável. F3-SECTORAL-BCB ainda marcava OLINDA
OData como DISCOVERED (SGS 432/433 já aprovados).

## Implementação

- Fonte `BCB-OLINDA-EXPECTATIVAS` (ExpectativasMercadoAnuais, allowlist IPCA).
- Conector `bcb_olinda_expectativas` / `parse_bcb_olinda_expectativas`.
- `$top`/`max_rows=8`, `baseCalculo=1`, valor `Mediana`.
- Fixture OData mínima + painel setorial + dashboard `/economia`.
- Migration `0069_bcb_olinda_expectativas` → `0.3.66`.

## Notas

Distinto de `BCB-SGS-OLINDA` (REST SGS). REFERENCE_QUANTITY. Sem crédito.
Sem carga ilimitada. Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
