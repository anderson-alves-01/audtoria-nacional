# Documentation-only production placeholder. terraform apply is forbidden.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

module "documentation_stack" {
  source      = "../../modules/documentation_stack"
  environment = "prod"
}
