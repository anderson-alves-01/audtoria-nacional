# Documentation-only stack. terraform apply is forbidden.

terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

variable "environment" {
  type        = string
  description = "Logical environment name. Never used to target a cloud account."
}

resource "null_resource" "placeholder" {
  triggers = {
    environment = var.environment
    purpose     = "documentation-only"
  }

  lifecycle {
    prevent_destroy = true
  }
}

output "apply_allowed" {
  value = false
}
