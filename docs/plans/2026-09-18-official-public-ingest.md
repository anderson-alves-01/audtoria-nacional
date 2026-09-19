# 0.3.14 — ingestão de fontes públicas oficiais (sem sintético operacional)

## Goal and user outcome

Persistir em Landing, Bronze, Silver e Gold somente dados obtidos de fontes oficiais `PUBLIC_OPEN` catalogadas. Dashboards exibem Gold oficial com homologação humana pendente, ou estado vazio. Fixtures sintéticas permanecem test-only.

## Roadmap phase and epic

Fase 3 / F3.1–F3.2 (ROADMAP 1.2). Spec `0.3.0`. Implementação `0.3.14`.

## Approved specification and ADR references

- `docs/delivery/ROADMAP-SIRTA-2026.md` § F3.0–F3.2 e diretórios oficiais.
- Instrução vinculante de 18/09/2026: uso exclusivo de dados reais oficiais.
- ADRs em `docs/architecture/` (nenhuma autorização de mock operacional).

## Components and exact files

- `contracts/sources/official-catalog.yaml`
- `apps/api/src/sirta_api/domain/catalog.py`
- `apps/api/src/sirta_api/application/catalog.py`
- `apps/api/src/sirta_api/application/official_ingest.py`
- `apps/api/src/sirta_api/application/source_ingest.py`
- `apps/api/src/sirta_api/adapters/ingest/`
- `apps/api/src/sirta_api/adapters/db/models.py` (`GoldOfficial`)
- `alembic/versions/0016_official_public_ingest.py`
- `apps/web/src/app/sources/`, `apps/web/src/app/funnel/`, `apps/web/src/app/health/`
- `tests/fixtures/official-snapshots/`
- `tests/unit/test_official_ingest.py`, `tests/integration/test_official_ingest.py`

## Consumed and produced interfaces

- Consome: IBGE Aggregates v3, SICONFI `/entes`, Tesouro Aria dicionário de transferências, documento Planalto EC 132 quando o HTTP oficial responder.
- Produz: `GET /v1/data-sources`, `POST .../ingest`, `GET /v1/indicators/official-gold`, Landing em `var/datalake/` (gitignored), manifests em `evidence/official-ingest/`.

## Data classification and allowed fixtures

- Operação: `PUBLIC_OPEN` somente após `PROVENANCE_VERIFIED` + `TECHNICALLY_APPROVED`.
- Testes: snapshots oficiais minimizados e mocks HTTP isolados. `SIRTA_ALLOW_SYNTHETIC_LOADS` só em pytest.
- Restrito/municipal/PII: `CREDENTIAL_REQUIRED`. Sem DPA, sem carga.

## Security and authorization impact

Ingestão oficial: `tech_admin`. Leitura Gold: papéis fiscais. Isolamento tenant/territory. CNPJ de ente público minimizado (não promovido a Silver/Gold).

## Migration and rollback strategy

Alembic `0016` aditivo (`create_all` + `gold_officials`). Rollback lógico: `published=false`. Sem drop.

## Acceptance criteria and evidence path

- Nenhum Gold de dashboard originado de fixture sintética.
- Cada Bronze com SHA-256, URL, HTTP status e manifesto.
- Silver com quarentena e reconciliação de contagens.
- Gold com fórmula, versão metodológica e `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.
- CI verde sem HTTP ao vivo.
- Evidência: `evidence/releases/0.3.14/` e `evidence/official-ingest/`.

## Human gates

Homologação tributária, jurídica, municipal, G0/G1/G4/G7-oficial/G8-oficial/G9/G10 permanecem BLOCKED. Nenhum estado `HOMOLOGATED`.
