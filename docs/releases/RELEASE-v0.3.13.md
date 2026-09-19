# Release v0.3.13 - Terraform documentation modules (no apply)

`infra/terraform/modules/documentation_stack` is consumed by local, dev, staging and prod placeholders. Provider is `hashicorp/null`. `prevent_destroy` stays on. `terraform apply` remains forbidden.

Spec 0.3.0 unchanged. Rollback: `git revert`. Migration `0015` additive.
