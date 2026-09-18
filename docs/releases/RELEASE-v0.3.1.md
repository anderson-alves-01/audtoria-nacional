# Release v0.3.1 - F0 Foundation local executable

## Objetivo

Entregar o núcleo local do SIRTA (implementation_version 0.3.1) sobre a especificação 0.3.0, sem reescrever `RELEASE-v0.3.0.md`.

`release_stage: F0_FOUNDATION`

## Escopo entregue

- Monorepo Git privado com LICENSE All Rights Reserved.
- FastAPI hexagonal, Angular 18 (Node 20 LTS pinado), worker, Compose local.
- PostgreSQL, Redis, Keycloak, MinIO. Dados exclusivamente sintéticos.
- OIDC local, RBAC/ABAC (analyst, validator, tech_admin sem conteúdo fiscal).
- Fail-closed para tenant, território e finalidade.
- Créditos apenas no estado IDENTIFIED. ValidateCredit e cobrança não são servidos.
- Auditoria imutável e redação de logs.
- CI sem credenciais de nuvem.

## Fora de escopo (permanece NO-GO / BLOQUEADO)

- G0 municipal (patrocinador, município piloto, diagnóstico homologado).
- ValidateCredit, cobrança, ISR, potencial, Gold, pipelines reais.
- Terraform cloud, GCP/AWS, dado fiscal real, produção.

## Rollback

```bash
docker compose down -v
git revert <sha-da-fatia>
```

## Evidências

`evidence/releases/0.3.1/`
