# 0.3.8 — saneamento Alembic e seed idempotente

## Goal and user outcome

Tornar `alembic upgrade` reproduzível em banco vazio, em `0004 -> head` válido e após testes que removem tabelas de domínio sem apagar `alembic_version`. Seed sintético deixa de viver em migrations mutáveis.

## Roadmap phase and epic

ROADMAP 1.2 dívida `KNOWN_DEBT/BLOCK_NEXT_RELEASE`. Sem nova funcionalidade de negócio nesta fatia.

## Approved specification

- AGENTS.md: migrations aditivas; jobs idempotentes.
- ROADMAP 1.2 § Dívida técnica obrigatória.
- Invariante: dados sintéticos somente.

## Components and files

- `alembic/versions/0003`–`0007` (schema only; seed removido)
- `alembic/versions/0010_alembic_hygiene.py`
- `apps/api/src/sirta_api/adapters/db/seed.py` (idempotente + `__main__`)
- `tests/conftest.py` (sem `drop_all`)
- `apps/api/Dockerfile`, `compose.yaml` (migrate/seed)
- `tests/integration/test_alembic_paths.py`

## Data classification

Somente IDs e créditos sintéticos já existentes.

## Security

Nenhuma rota nova. Seed não registra dado real.

## Migration and rollback

`0010` aditivo (`schema_meta` 0.3.8). Rollback: `git revert`. Não dropar `alembic_version` em `sirta`. Banco `sirta_migtest` é isolado para provas de caminho.

## Acceptance

- Falha 0004→0005 reproduzida em evidência (antes do fix).
- `base -> head` em banco vazio.
- `0004 -> head` com seed válido.
- `0004 -> head` após `drop_all` das tabelas de domínio.
- Seed executado duas vezes sem duplicar.
- Compose declara serviço `migrate` e a API aplica seed após migrate.
- pytest não usa `Base.metadata.drop_all` no banco compartilhado.

## Evidence path

`evidence/releases/0.3.8/`

## Human gates

Inalterados (G0/G1/G4/G7 oficial/G8 oficial/G9/G10 BLOCKED).
