# Documentation-only local stack. terraform apply is forbidden.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

resource "null_resource" "local_placeholder" {
  triggers = {
    purpose = "documentation-only"
  }

  lifecycle {
    prevent_destroy = true
  }
}
