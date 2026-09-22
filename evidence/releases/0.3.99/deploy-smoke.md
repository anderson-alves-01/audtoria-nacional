# Evidência redeploy 0.3.99 — dashboards premium

## Imagens

- ECR `sirta-prod-api:0.3.99`
- ECR `sirta-prod-web:0.3.99` (nginx.prod.conf)
- Task definitions: `sirta-prod-api:3`, `sirta-prod-web:3`
- Cluster `sirta-prod` services stable

## Smoke

- ALB: `http://sirta-prod-alb-1369017354.sa-east-1.elb.amazonaws.com`
- `/health` → `implementationVersion` **0.3.99**
- `/`, `/executivo`, `/financeiro`, `/transferencias`, `/cobranca` → 200
- Evidence: `evidence/ops/smoke-prod-20260921T211940Z.txt`
- Redeploy log: `evidence/ops/ecs-redeploy-0.3.99.txt`

## Status

- Gold referência: `REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY`
- Sem crédito; G0/G1/G4/G9 inalterados; sem merge `main`
