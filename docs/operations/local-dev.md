# Ambiente local SIRTA (implementation 0.3.1)

Somente dados sintéticos. Não conectar a projetos GCP/AWS nem carregar bases municipais.

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
| PostgreSQL | 5432 | Transacional |
| Redis | 6379 | Cache sem PII persistente |
| MinIO S3 | 9000 | Storage local |
| MinIO console | 9001 | Console local |
| Keycloak | 8081 | OIDC local (`/realms/sirta`) |

Usuários sintéticos Keycloak: `analyst.alpha`, `validator.alpha`, `admin.alpha`, `analyst.beta`. Senha local: `synthetic`.

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
