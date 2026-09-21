# Verdict 0.3.65

## Fatia

Tesouro COINT restante por município: FPM, ITR, IOF-Ouro e LC 176/2020
via `tesouro_coint_municipio_csv` (PUBLIC_OPEN).

## Evidência

- Unit + integration: ver `tests.txt`
- Fonte: PUBLIC_OPEN; fixtures mínimas latin-1; sem crédito
- Distintos dos CSV mensais homônimos
- Migration: `0068_tesouro_coint_remaining` → implementation_version `0.3.65`
- Gold: `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`

## Rollback

Reverter migration para `0067_tesouro_lc87_coint` e remover as quatro fontes
COINT novas do catálogo/runtime.
