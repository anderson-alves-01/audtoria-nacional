# RELEASE NOTES 0.3.65

## Fatia

Ativação dos CSVs COINT restantes do Tesouro Transparente (FPM, ITR,
IOF-Ouro e LC 176/2020 por município), reutilizando
`tesouro_coint_municipio_csv`. Distintos dos allowlists mensais
`TESOURO-*-VALORES`.

## Entregas

- Fontes `TESOURO-FPM-COINT-VALORES`, `TESOURO-ITR-COINT-VALORES`,
  `TESOURO-IOF-OURO-COINT-VALORES`, `TESOURO-LC176-COINT-VALORES`.
- Fixtures oficiais mínimas + testes de parser e ingest.
- Migration Alembic `0068_tesouro_coint_remaining` →
  `implementation_version=0.3.65`.
- Pacote COINT municipal do dataset Transferências Obrigatórias completo.

## Restrições

- `max_rows=8`; sem carga nacional dos CSV grandes.
- Fonte pública não cria crédito.
- Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
