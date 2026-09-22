# Ciclo autônomo 0.3.50 — ES IPI/CIDE + GO IPI

- Branch: `feat/official-public-ingest`
- PR: #2
- Resultado: `PROGRESSED`
- Evidência: `evidence/releases/0.3.50/`

## Seleção

UFs restantes sem CSV/API recente (re-probe 0.3.49). Fatia segura: profundidade D9 nos arquivos já aprovados de ES e GO.

## Entrega

- Parsers: `parse_state_es_csv` (IPI, CIDE); `parse_state_go_economia_xlsx` (IPI / IPI-Exportação).
- Catálogo oficial + state-transfers; Gold presentation; dashboard transferências.
- Testes unitários e de integração; Alembic `0053`.

## Gates

Humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados. Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
