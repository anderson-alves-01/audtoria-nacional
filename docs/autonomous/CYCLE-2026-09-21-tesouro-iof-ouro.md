# Ciclo autônomo 0.3.53 — Tesouro IOF-Ouro

- Branch: `feat/official-public-ingest`
- PR: #2
- Resultado: `PROGRESSED`
- Evidência: `evidence/releases/0.3.53/`

## Seleção

UFs restantes sem CSV/API recente. Fatia segura: allowlist IOF-Ouro no CSV mensal Tesouro (31 linhas no probe 202609). CIDE/FEX ausentes nesse arquivo.

## Entrega

- Fonte `TESOURO-IOF-OURO-VALORES` (`transfer_item_allowlist: ["IOF Ouro"]`).
- Testes unitários e integração; Alembic `0056`.

## Gates

Humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 inalterados. Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
