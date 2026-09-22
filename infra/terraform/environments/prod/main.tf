# Production environment for SIRTA.
# Real AWS resources are created ONLY when cloud_apply_authorized = true (G10).
# Default is false: documentation placeholder only — no paid resources.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Local state by default. Remote backend is configured only after G10 authorization.
  # backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  # CI plan with cloud_apply_authorized=false must not require real AWS credentials.
  skip_credentials_validation = !var.cloud_apply_authorized
  skip_requesting_account_id  = !var.cloud_apply_authorized
  skip_metadata_api_check     = !var.cloud_apply_authorized

  default_tags {
    tags = local.tags
  }
}

variable "cloud_apply_authorized" {
  type        = bool
  description = "G10 gate. Must be true only after written authorization. Default false."
  default     = false
}

variable "aws_region" {
  type    = string
  default = "sa-east-1"
}

variable "aws_account_id" {
  type        = string
  description = "Expected AWS account ID. Empty skips the account guard."
  default     = ""
}

variable "name_prefix" {
  type    = string
  default = "sirta-prod"
}

variable "acm_certificate_arn" {
  type    = string
  default = ""
}

variable "api_image" {
  type    = string
  default = ""
}

variable "web_image" {
  type    = string
  default = ""
}

variable "worker_image" {
  type    = string
  default = ""
}

variable "budget_limit_usd" {
  type    = number
  default = 200
}

variable "budget_notification_email" {
  type    = string
  default = ""
}

data "aws_caller_identity" "current" {
  count = var.cloud_apply_authorized ? 1 : 0
}

locals {
  enabled = var.cloud_apply_authorized
  caller_account_id = var.cloud_apply_authorized ? data.aws_caller_identity.current[0].account_id : ""
  tags = {
    project = "auditoria-nacional"
    env     = "prod"
    purpose = "public-open-validation"
    g10     = var.cloud_apply_authorized ? "authorized" : "blocked"
  }
}

resource "null_resource" "g10_gate" {
  triggers = {
    authorized = tostring(var.cloud_apply_authorized)
    account    = local.caller_account_id == "" ? "gated-off" : local.caller_account_id
    region     = var.aws_region
  }

  lifecycle {
    precondition {
      condition     = var.aws_account_id == "" || local.caller_account_id == "" || var.aws_account_id == local.caller_account_id
      error_message = "AWS account mismatch. Set aws_account_id to the authorized production account."
    }
    precondition {
      condition     = var.cloud_apply_authorized == false || var.aws_account_id != ""
      error_message = "cloud_apply_authorized=true requires aws_account_id to be set explicitly."
    }
  }
}

# Keep a documentation-only marker when apply is not authorized (destroyable when G10 opens).
resource "null_resource" "documentation_only" {
  count = local.enabled ? 0 : 1
  triggers = {
    environment = "prod"
    purpose     = "documentation-only-until-g10"
  }
}

module "networking" {
  source      = "../../modules/networking"
  enabled     = local.enabled
  name_prefix = var.name_prefix
  tags        = local.tags
}

module "data" {
  source                = "../../modules/data"
  enabled               = local.enabled
  name_prefix           = var.name_prefix
  private_subnet_ids    = module.networking.private_subnet_ids
  rds_security_group_id = module.networking.rds_security_group_id == null ? "" : module.networking.rds_security_group_id
  tags                  = local.tags
}

module "compute" {
  source                = "../../modules/compute"
  enabled               = local.enabled
  name_prefix           = var.name_prefix
  vpc_id                = module.networking.vpc_id == null ? "" : module.networking.vpc_id
  public_subnet_ids     = module.networking.public_subnet_ids
  private_subnet_ids    = module.networking.private_subnet_ids
  alb_security_group_id = module.networking.alb_security_group_id == null ? "" : module.networking.alb_security_group_id
  ecs_security_group_id = module.networking.ecs_security_group_id == null ? "" : module.networking.ecs_security_group_id
  database_secret_arn   = module.data.database_secret_arn == null ? "" : module.data.database_secret_arn
  landing_bucket_name   = module.data.landing_bucket_name == null ? "" : module.data.landing_bucket_name
  acm_certificate_arn   = var.acm_certificate_arn
  api_image             = var.api_image
  web_image             = var.web_image
  worker_image          = var.worker_image
  tags                  = local.tags
}

module "observability" {
  source                    = "../../modules/observability"
  enabled                   = local.enabled
  name_prefix               = var.name_prefix
  budget_limit_usd          = var.budget_limit_usd
  budget_notification_email = var.budget_notification_email
  tags                      = local.tags
}

output "apply_allowed" {
  value = var.cloud_apply_authorized
}

output "aws_account_id" {
  value = local.caller_account_id == "" ? null : local.caller_account_id
}

output "aws_region" {
  value = var.aws_region
}

output "alb_dns_name" {
  value = module.compute.alb_dns_name
}

output "ecr_api_url" {
  value = module.compute.ecr_api_url
}

output "ecr_web_url" {
  value = module.compute.ecr_web_url
}

output "ecr_worker_url" {
  value = module.compute.ecr_worker_url
}

output "landing_bucket_name" {
  value = module.data.landing_bucket_name
}

output "database_secret_arn" {
  value = module.data.database_secret_arn
}

output "rollback_notes" {
  value = "See docs/ops/PROD-RUNBOOK.md. Destroy requires dual confirmation; take RDS snapshot first."
}
