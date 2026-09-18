# Ambiente local SIRTA (implementation 0.3.1)

Não conectar a projetos GCP/AWS nem carregar bases municipais.

PostgreSQL é publicado em `localhost:55432` para evitar colisão com outro Postgres na 5432.

## Subir

```bash
cp .env.example .env
docker compose up --build
```

## Portas

| Serviço | Porta | Uso |
|---|---|---|
| API | 8080 | FastAPI |
| Web | 4200 | Angular (após S0.5) |
| PostgreSQL | 55432 | Transacional (host; container 5432) |
| Redis | 6379 | Cache sem PII persistente |
| MinIO S3 | 9000 | Storage local |
| MinIO console | 9001 | Console local |
| Keycloak | 8081 | OIDC local (`/realms/sirta`) |

Usuários sintéticos Keycloak: `analyst.alpha`, `validator.alpha`, `admin.alpha`, `analyst.beta`. Senha local: `synthetic`.

Validação: `POST /v1/tax-credits/{id}/validations` (validador). Cobrança permanece 404.

## Rollback

```bash
docker compose down -v
```

Remove containers e volumes locais. Não há recurso cloud para destruir.

Rollback de código da fatia correspondente:

```bash
git revert <sha>
```

Não usar `git reset --hard` nem force push.
