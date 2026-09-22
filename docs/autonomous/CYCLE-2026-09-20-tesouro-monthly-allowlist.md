# Ciclo autônomo 0.3.51 — Tesouro ITR / IPI-EXP / Royalties

- Branch: `feat/official-public-ingest`
- PR: #2
- Resultado: `PROGRESSED`
- Evidência: `evidence/releases/0.3.51/`

## Seleção

UFs restantes sem CSV/API recente. Fatia segura: allowlist no CSV mensal Tesouro já usado pelo FPM (ITR, IPI-EXP, Royalties).

## Entrega

- `parse_tesouro_monthly_csv` com `transfer_item_allowlist` / `transfer_destination_allowlist`.
- Fontes `TESOURO-ITR-VALORES`, `TESOURO-IPI-EXP-VALORES`, `TESOURO-ROYALTIES-VALORES`.
- Testes unitários e integração; Alembic `0054`.

## Gates

Humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados. Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
