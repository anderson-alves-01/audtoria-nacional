# Runbook produção SIRTA (AWS)

## Escopo

Ambiente `prod` em AWS para validar shells + dados `PUBLIC_OPEN`.  
Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.  
Não promove crédito, não faz merge em `main`, não carrega dados municipais restritos.

## Pré-requisitos

1. `DOC-HOMOLOGATION-PACKAGE` = `TECH_COMPLETE`.
2. Autorização G10 escrita em `docs/ops/G10-AUTHORIZATION.md` / conversa.
3. Credenciais AWS no principal de deploy (ex.: `TerraformUser`).
4. Docker local para build/push ECR após apply da infra base.

## Stack

- VPC + subnets públicas/privadas + NAT
- RDS Postgres 16 criptografado + Secrets Manager
- S3 landing (block public)
- ECR + ECS Fargate (`api`, `web`, `worker`) + ALB
- CloudWatch logs/alarmes + budget mensal

Código: `infra/terraform/environments/prod`.  
Gate: `cloud_apply_authorized` (default `false`).

## Plan (sempre primeiro)

```powershell
tools/ops/prod-terraform.ps1 -Action Plan
```

Arquiva saída em `evidence/ops/`.

## Apply (somente com G10)

```powershell
tools/ops/prod-terraform.ps1 -Action Apply `
  -AccountId 332380491162 `
  -Region sa-east-1 `
  -AuthorizationPhrase "autorizo terraform apply em produção nesta conta/região"
```

## Rollback

1. Snapshot RDS manual antes de destroy/migração destrutiva.
2. `terraform plan -destroy` revisado.
3. Dupla confirmação humana; nunca `destroy` automático no CI.
4. Re-deploy de imagens ECR por tag imutável anterior.
5. Manter `deletion_protection = true` no RDS até decisão explícita.

## Smoke pós-deploy

```powershell
tools/ops/prod-smoke.ps1 -BaseUrl https://<alb-dns>
```

Verifica `/health` e home web. Não valida Gold.

## Proibições

- Promover Gold / `homologated=true`
- Carga RFB nacional
- Conectores `CREDENTIAL_REQUIRED` sem DPA
- Commit de `terraform.tfvars` com secrets ou `cloud_apply_authorized=true`
