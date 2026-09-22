# Ciclo autônomo 0.3.54 — Tesouro COINT CIDE/FEX

- Branch: `feat/official-public-ingest`
- PR: #2
- Resultado: `PROGRESSED`
- Evidência: `evidence/releases/0.3.54/`

## Seleção

UFs restantes sem CSV/API recente. Fatia segura: dataset CKAN
`transferencias-obrigatorias-da-uniao-por-municipio` com CSV wide
`cide-por-municipio.csv` e `fex-por-municipio.csv` (PUBLIC_OPEN, ODbL).

## Entrega

- Conector `tesouro_coint_municipio_csv`.
- Fontes `TESOURO-CIDE-VALORES` e `TESOURO-FEX-VALORES`.
- Testes unitários/integração; Alembic `0057`.

## Gates

Humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados. Gold
`REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
