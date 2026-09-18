# Release v0.3.10 - program gates snapshot and Terraform docs

GET `/v1/program-gates` exposes LOCAL_GO / OFFICIAL_BLOCKED / BLOCKED without fabricating approval. Feature flags remain false. `infra/terraform/environments/local` is documentation-only (`prevent_destroy`, no cloud provider).

Spec 0.3.0 unchanged. Rollback: `git revert`. Migration `0012` additive.
