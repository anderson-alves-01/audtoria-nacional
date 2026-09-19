# 0.3.15 — correção de estado e continuidade do ROADMAP

## Goal and user outcome

Corrigir o estado prematuro da onda 1 e avançar itens técnicos implementáveis do ROADMAP 1.2 com dados oficiais apenas, dashboards obrigatórios e conectores vazios onde a fonte não estiver ativável.

## Roadmap phase and epic

F3.2 continuação, F3.3 contratos, F4–F8 esqueletos técnicos, G7 investigação de valores, G8 documental.

## Approved specification and ADR references

- `docs/delivery/ROADMAP-SIRTA-2026.md`
- Instrução de correção de 19/09/2026: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Components and exact files

- `current-state.yaml`, `MANIFEST.md`, `docs/delivery/ROADMAP-SIRTA-2026.md`
- `apps/api` ingestão FPM/RREO/documentos/estadual/RFB
- `apps/web` 15 dashboards
- `alembic/versions/0018_roadmap_continuation.py`
- `tests/unit/test_gold_invariants.py`, `tests/integration/test_gold_lineage.py`

## Consumed and produced interfaces

Consome APIs/arquivos PUBLIC_OPEN. Produz Gold com lineage por linha, painéis e estados vazios documentados.

## Data classification and allowed fixtures

PUBLIC_OPEN operacional. RESTRICTED permanece CREDENTIAL_REQUIRED. Snapshots oficiais só em testes.

## Security and authorization impact

Ingestão tech_admin. Leitura fiscal. Sem crédito a partir de fonte pública. Sem PII de EI.

## Migration and rollback strategy

0018 aditivo. Rollback lógico `published=false`. Sem drop.

## Acceptance criteria and evidence path

Estado `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS` até o roadmap técnico restante estar coberto. Evidência `evidence/releases/0.3.15/`.

## Human gates

G0/G1/G4/G7-oficial/G8-oficial/G9/G10 permanecem BLOCKED. Sem merge em main.
