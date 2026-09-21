# Evidência apply PROD autorizado (G10)

## Autorização

- Frase: `autorizo terraform apply em produção nesta conta 332380491162, região sa-east-1`
- Conta: `332380491162`
- Região: `sa-east-1`
- Principal: `TerraformUser`

## Resultado infra

- `terraform apply`: **51 resources added**
- Imagens ECR tag `0.3.98` (api/web/worker) enviadas
- Task definitions atualizadas; web corrigido com `nginx.prod.conf` (sem upstream `api`)
- Smoke: `/health` **200**, `/` **200**
- ALB: `http://sirta-prod-alb-1369017354.sa-east-1.elb.amazonaws.com`
- Gold: **não** promovido (`PENDING_HUMAN_VALIDATION`)
- Merge `main`: não realizado

## Arquivos

- `evidence/ops/terraform-apply-prod-20260921T200205Z.txt`
- `evidence/ops/terraform-apply-prod-images-0.3.98.txt`
- `evidence/ops/smoke-prod-20260921T202507Z.txt`
