# F0 Foundation — núcleo local seguro (implementation 0.3.1)

## Goal and user outcome

Disponibilizar um monorepositório local reproduzível do SIRTA no qual um servidor municipal autentica via OIDC, opera com contexto obrigatório de tenant, território e finalidade, e consulta ou registra créditos **identificados** sintéticos sem validar, cobrar ou publicar indicador.

Outcome: `docker compose up` sobe API, web, worker, PostgreSQL, Redis, Keycloak e MinIO; testes negativos de isolamento falham se o middleware for removido; nenhuma nuvem ou dado real é usado.

## Roadmap phase and epic

- Roadmap vigente: `docs/delivery/ROADMAP-SIRTA-2026.md` (G2 Fundação tecnológica).
- Roadmap legado: `docs/delivery/ROADMAP.md`.
- Fase técnica: `F0_FOUNDATION`.
- Release de especificação: `spec_version: 0.3.0` (`docs/releases/RELEASE-v0.3.0.md` não será reescrita).
- Release de implementação: `implementation_version: 0.3.1`.
- `release_stage: F0_FOUNDATION`.
- Épicos: `EP-SIRTA-001` (Sprint 0) e `EP-SIRTA-002` (Sprint 1).
- Fora de escopo: G0 municipal, EP-SIRTA-003+, ValidateCredit, cobrança, Gold/ISR/potencial, Terraform cloud.

## Approved specification and ADR references

- Auditoria F0 aprovada em 2026-09-18.
- `AGENTS.md`, `docs/architecture/DECISIONS.md` (ADR-001 a ADR-007).
- `docs/architecture/SIRTA-DOMAIN.md`, `docs/security/ROLE-MATRIX.md`, `docs/security/SECURITY.md`.
- `docs/delivery/SPRINT-PLAN-v0.3.md` sprints 0 e 1.
- `docs/delivery/TEST-STRATEGY-v0.3.md`.
- Contrato ativo: `contracts/openapi/sirta-v1.yaml`.
- `contracts/openapi/api-outline.yaml` permanece legado/depreciado.

## Components and exact files

| Componente | Arquivos |
|---|---|
| Git / licença | `.gitignore`, `.gitattributes`, `LICENSE`, `.env.example` |
| Python API | `pyproject.toml`, `apps/api/src/sirta_api/**`, `apps/api/Dockerfile`, `alembic.ini`, `alembic/**` |
| Worker | `apps/workers/src/sirta_workers/**`, `apps/workers/Dockerfile` |
| Web | `apps/web/**`, `.nvmrc` |
| Compose | `compose.yaml`, `infra/keycloak/realm-sirta.json`, `infra/postgres/init.sql` |
| Testes | `tests/unit/**`, `tests/integration/**`, `tests/contract/**`, `tests/security/**`, `tests/fixtures/**` |
| CI | `.github/workflows/ci.yml` |
| Contratos | `contracts/openapi/sirta-v1.yaml`, `contracts/openapi/api-outline.yaml` |
| Docs | `README.md`, `MANIFEST.md`, `docs/delivery/BACKLOG.md`, `backlog/SIRTA-v0.3.yaml`, `docs/operations/local-dev.md`, `docs/releases/RELEASE-v0.3.1.md` |
| Evidência | `evidence/releases/0.3.1/**` |

## Consumed and produced interfaces

Consumidos: OpenAPI SIRTA v1, JSON Schema de crédito, realm Keycloak local, PostgreSQL 16, Redis 7, MinIO.

Produzidos:

- `GET /health` (público)
- `GET /ready` (público; 503 se o banco estiver indisponível)
- `GET/POST /v1/tax-credits`, `GET /v1/tax-credits/{creditId}` (protegidos; crédito permanece `IDENTIFIED`)
- `GET /v1/audit-events` (protegido)
- Eventos de auditoria imutáveis sem PII
- Cliente Angular 18 que exibe saúde da API e lista créditos autorizados

Não produzidos: `/validations`, `/collection-cases`, ISR, transferências, pipelines.

## Data classification and allowed fixtures

Classificação: sintético, não pessoal, uso local/CI.

Fixtures fixas em `tests/fixtures/synthetic.py` e seed Alembic/SQL: dois tenants (`alpha`, `beta`), territórios, usuários `analyst` / `validator` / `tech_admin`, finalidade ativa e expirada, dois créditos identificados. Nenhum CPF/CNPJ real. Valores regionais em reais citados em `docs/product/REGIONAL-PLAN.md` permanecem hipóteses e não entram em KPI.

## Security and authorization impact

- Default deny. OIDC local (Keycloak) ou JWKS de teste.
- Claims/contexto obrigatórios: `tenant_id`, `territory_id` (`X-Territory-Id`), `purpose_id` (`X-Purpose-Id`).
- Falha fechada (401 token inválido; 403 RFC 9457 para papel, território, finalidade ou tenant divergente).
- Recurso de outro tenant: 404 (não revela existência).
- `tech_admin` não lê nem grava conteúdo fiscal.
- Logs JSON sem token, CPF/CNPJ, corpo fiscal ou Authorization.
- Segredos só em `.env` (gitignorado). Compose usa senhas locais explícitas, nunca de produção.

## Migration and rollback strategy

- Alembic aditivo: identidade, vínculos território-usuário, finalidades, créditos identificados, auditoria.
- Rollback operacional: `docker compose down -v` descarta volumes locais.
- Rollback de código: `git revert <sha-da-fatia>` (não usar reset --hard nem force push).
- Nenhuma migration remove coluna nesta fase.

## Acceptance criteria and evidence path

Critérios da auditoria F0, evidência em `evidence/releases/0.3.1/`:

1. Git inicializado após confirmar ausência de repositório pai; `.gitignore` cobre `.env`, secrets, volumes, `node_modules`, IDE.
2. Compose sobe a pilha com dados sintéticos.
3. `/health` 200; `/ready` 200 com banco; `/ready` 503 com banco indisponível.
4. CI: format, lint Python, testes Python, lint OpenAPI, secret scan, build/test Angular, build de containers; zero credencial cloud.
5. Consulta fiscal recusada sem tenant, território ou finalidade válidos.
6. Testes cross-tenant, território negado, finalidade expirada, papel insuficiente e IDOR verdes; ficam vermelhos se o middleware de contexto for removido.
7. Logs das suítes sem token ou identificador pessoal completo.
8. Rollback documentado.
9. `current-state.yaml` atualizado somente após os gates.

## Human gates

Não cruzar: credenciais reais, dado fiscal real, IAM cloud, recurso pago, Terraform prod, publicação externa, G0 municipal, interpretação jurídico-tributária, ValidateCredit, cobrança.

## Tasks

### S0.1 Git e licença

Arquivos: `.gitignore`, `.gitattributes`, `LICENSE` (All Rights Reserved), este plano.
Comando: verificar repositório pai; `git init` somente se ausente.
Esperado: working tree rastreável, LICENSE proprietária.
Rollback: não há remoto; não apagar `.git` após o primeiro commit útil.

### S0.2 Workspace Python

Arquivos: `pyproject.toml`, pacote hexagonal, teste unitário de `/health`.
Comando: `python -m pytest tests/unit/test_health.py`.
Esperado: RED então GREEN; health 200 com `specVersion` 0.3.0 e `implementationVersion` 0.3.1.

### S0.3 Compose

Arquivos: `compose.yaml`, realm Keycloak, `.env.example`, `docs/operations/local-dev.md`.
Comando: `docker compose config`.
Esperado: serviços postgres, redis, minio, keycloak, api, web, worker sem registry cloud privado.

### S0.4 Observabilidade e prontidão

Arquivos: `/ready`, logs JSON, `trace_id`, Alembic bootstrap.
Comando: pytest de readiness 200 e 503.
Esperado: 503 quando `DATABASE_URL` aponta para host recusado.

### S0.5 Angular 18

Arquivos: `apps/web`, `.nvmrc` (`20.19.0`), `engines.node` `>=20.19.0 <21`.
Comando: `npm test` e `npm run build` com a constraint documentada.
Esperado: componente de saúde com estados loading/erro/ok.

### S0.6 CI

Arquivo: `.github/workflows/ci.yml`.
Esperado: jobs sem `GCP_`, `AWS_`, `TF_VAR_` secrets; postgres de serviço apenas.

### S1.1 Identidade

Migration e modelos Organization, Tenant, Territory, User, Role, AccessPurpose.
Comando: `alembic upgrade head` + testes de persistência.

### S1.2 OIDC e contexto

Middleware/dependency fail-closed.
Comando: testes 401 sem token e 403 sem finalidade.

### S1.3 RBAC/ABAC

Papéis analyst, validator, tech_admin.
Comando: admin técnico recebe 403 em GET `/v1/tax-credits`.

### S1.4 Isolamento

Tenant incorreto, território negado, finalidade expirada, IDOR, prova de que remover a dependency quebra os testes.
Comando: `python -m pytest tests/security`.

### S1.5 Auditoria e logs

Eventos imutáveis; teste de redação.
Comando: pytest de audit + scanner de logs da suíte.

### Documentação e evidência

Atualizar README, MANIFEST, BACKLOG, ROADMAP legado, `current-state.yaml` somente com gates verdes. Salvar saídas em `evidence/releases/0.3.1/`.
