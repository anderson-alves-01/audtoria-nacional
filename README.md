# Auditoria Nacional - SIRTA Municipal

Plataforma segura de inteligência fiscal, auditoria e recuperação de receitas municipais.

**Especificação:** 0.3.0 (`docs/releases/RELEASE-v0.3.0.md`, não reescrita).  
**Implementação local:** 0.3.2 (`docs/releases/RELEASE-v0.3.2.md`).  
**Fase:** Sprint 2 validação (F0 local permanece verde). **Roadmap vigente:** `docs/delivery/ROADMAP-SIRTA-2026.md`.  
`docs/delivery/ROADMAP.md` é legado.

## Execução local (sintético)

```bash
cp .env.example .env
docker compose up -d postgres redis
alembic upgrade head
python -m pip install -e ".[dev]"
python -m pytest tests -q
uvicorn sirta_api.entrypoints.main:app --host 0.0.0.0 --port 8080
```

Portal Angular (Node 20.19.0; engines `>=20.19.0 <21`):

```bash
cd apps/web
npm ci
npm test
npm start
```

Pilha completa: `docker compose up --build`.

Validação (validador sintético, checklist `credit-legality-v1`):

```http
POST /v1/tax-credits/{creditId}/validations
Idempotency-Key: <16+ chars>
```

Cobrança administrativa permanece **não implementada**.

PostgreSQL no host usa a porta **55432** para não colidir com outros servidores locais.

## Portas

| Serviço | Porta |
|---|---|
| API | 8080 |
| Web | 4200 |
| PostgreSQL (host) | 55432 |
| Redis | 6379 |
| MinIO | 9000 / 9001 |
| Keycloak | 8081 |

## Rollback

```bash
docker compose down -v
git revert <sha>
```

## Cursor

1. `AGENTS.md` e `current-state.yaml`
2. Auditoria: `prompts/00-bootstrap-audit.md`
3. Implementação F0 e Sprint 2 de validação nesta árvore. Não usar `prompts/01-master-autonomous-loop.md` até nova autorização além da Sprint 2.
4. Próxima fase (Sprint 3 cobrança) só com autorização explícita.

G0 municipal (patrocinador, município piloto, diagnóstico) **não** está concluído.
