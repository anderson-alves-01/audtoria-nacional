# 0.3.13 — módulos Terraform documentation-only (sem apply)

## Goal and user outcome

Organizar `infra/terraform` em módulo reutilizável e ambientes local/dev/staging/prod sem provider de nuvem, sem credencial e sem `apply`.

## Roadmap phase and epic

Plataforma local. G10 permanece BLOCKED.

## Approved specification

- ROADMAP 1.2: Terraform generate/validate; apply proibido.
- Skill devops-platform: CI valida sem credencial de nuvem.
- Skill validation-first: asserts de política antes da config.

## Components

- `infra/terraform/modules/documentation_stack/`
- `infra/terraform/environments/{local,dev,staging,prod}/main.tf`
- `tests/unit/test_terraform_local.py` (todos os ambientes)
- Alembic `0015` bump 0.3.13

## Security

Nenhum provider GCP/AWS/Azure. `prevent_destroy`. Comentário `apply is forbidden`. Sem secrets.

## Migration

`0015_terraform_modules` aditivo (schema_meta 0.3.13). Sem tabela nova.

## Acceptance

- Todos os `.tf` sem `google`, `aws_`, `azurerm`
- Ambientes referenciam o módulo
- Testes unitários verdes; nenhum `terraform apply`

## Evidence

`evidence/releases/0.3.13/`

## Human gates

G10, cloud apply, IAM real: BLOCKED.
