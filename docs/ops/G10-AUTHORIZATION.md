# Autorização G10 — deploy AWS produção

Este arquivo **não** desbloqueia `terraform apply` sozinho. Exige ato explícito do responsável.

## Conta descoberta (somente leitura)

| Campo | Valor |
|---|---|
| Account ID | `332380491162` |
| IAM principal observado | `arn:aws:iam::332380491162:user/TerraformUser` |
| Região padrão do plano | `sa-east-1` |
| Região default do CLI local | `us-east-1` (confirmar na autorização) |

Verificado com `aws sts get-caller-identity` em 2026-09-21. Nenhuma mutação foi executada.

## Texto obrigatório para autorizar apply

Cole nesta conversa (ou anexe evidência versionada) **exatamente**:

> autorizo terraform apply em produção nesta conta/região

Informando também:

1. Conta: `332380491162` (ou outra)
2. Região: `sa-east-1` (ou outra)
3. Confirmação de que o principal IAM tem permissão mínima de deploy

## Estado

- `cloud_apply_authorized` no Terraform PROD: **false** (default)
- Gate `g10_production` em `current-state.yaml`: **NO-GO**
- Gold: permanece `PENDING_HUMAN_VALIDATION`

## Após autorização

1. Preencher `infra/terraform/environments/prod/terraform.tfvars` a partir do example (não commitar secrets).
2. Executar `tools/ops/prod-terraform.ps1 -Action Plan`.
3. Revisar plan em `evidence/ops/`.
4. Executar `tools/ops/prod-terraform.ps1 -Action Apply` com frase e conta/região.
5. Smoke: `tools/ops/prod-smoke.ps1`.
