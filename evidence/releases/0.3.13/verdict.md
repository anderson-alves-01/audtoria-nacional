GO for 0.3.13 Terraform documentation modules.

- 99 pytest passed; Alembic head `0015_terraform_modules`.
- 15 Angular tests SUCCESS.
- Module `documentation_stack` uses hashicorp/null, prevent_destroy, apply forbidden.
- Environments local/dev/staging/prod consume the module. No google/aws/azurerm.
- `terraform validate` succeeded with `-backend=false`. No apply, no cloud credentials.
- Human gates G0/G1/G4/G7-official/G8-official/G9/G10 remain BLOCKED.
