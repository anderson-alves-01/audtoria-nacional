# RELEASE NOTES 0.3.98

## Inclui

- Consolidação técnica de `DOC-HOMOLOGATION-PACKAGE` (`TECH_COMPLETE`; Gold ainda pendente de humanos).
- Stack Terraform de produção real (networking, data, compute, observability) com gate `cloud_apply_authorized` default `false`.
- Runbooks e scripts `tools/ops/prod-terraform.ps1` / `prod-smoke.ps1`.
- Workflows `terraform-prod-check` e `deploy-prod` (environment GitHub `production`, sem apply automático).

## Não inclui

- `terraform apply` / recursos pagos criados.
- Homologação humana de Gold.
- Merge em `main`.
- Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 liberados.
