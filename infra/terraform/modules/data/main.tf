# Production data plane — RDS Postgres, S3 landing, Secrets Manager.
# Paid resources only when var.enabled = true.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

variable "enabled" {
  type = bool
}

variable "name_prefix" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "rds_security_group_id" {
  type = string
}

variable "db_username" {
  type    = string
  default = "sirta"
}

variable "tags" {
  type    = map(string)
  default = {}
}

resource "random_password" "db" {
  count            = var.enabled ? 1 : 0
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_db_subnet_group" "this" {
  count      = var.enabled ? 1 : 0
  name       = "${var.name_prefix}-db"
  subnet_ids = var.private_subnet_ids
  tags       = merge(var.tags, { Name = "${var.name_prefix}-db-subnets" })
}

resource "aws_db_instance" "postgres" {
  count                      = var.enabled ? 1 : 0
  identifier                 = "${var.name_prefix}-pg"
  engine                     = "postgres"
  engine_version             = "16"
  instance_class             = "db.t4g.micro"
  allocated_storage          = 20
  max_allocated_storage      = 100
  storage_encrypted          = true
  db_name                    = "sirta"
  username                   = var.db_username
  password                   = random_password.db[0].result
  db_subnet_group_name       = aws_db_subnet_group.this[0].name
  vpc_security_group_ids     = [var.rds_security_group_id]
  publicly_accessible        = false
  multi_az                   = false
  backup_retention_period    = 7
  deletion_protection        = true
  skip_final_snapshot        = false
  final_snapshot_identifier  = "${var.name_prefix}-pg-final"
  auto_minor_version_upgrade = true
  tags                       = merge(var.tags, { Name = "${var.name_prefix}-pg" })
}

resource "aws_secretsmanager_secret" "db" {
  count = var.enabled ? 1 : 0
  name  = "${var.name_prefix}/database"
  tags  = var.tags
}

resource "aws_secretsmanager_secret_version" "db" {
  count     = var.enabled ? 1 : 0
  secret_id = aws_secretsmanager_secret.db[0].id
  secret_string = jsonencode({
    username     = var.db_username
    password     = random_password.db[0].result
    host         = aws_db_instance.postgres[0].address
    port         = aws_db_instance.postgres[0].port
    dbname       = "sirta"
    database_url = "postgresql+psycopg://${var.db_username}:${random_password.db[0].result}@${aws_db_instance.postgres[0].address}:5432/sirta"
  })
}

resource "aws_s3_bucket" "landing" {
  count  = var.enabled ? 1 : 0
  bucket = "${var.name_prefix}-landing"
  tags   = merge(var.tags, { Name = "${var.name_prefix}-landing" })
}

resource "aws_s3_bucket_public_access_block" "landing" {
  count                   = var.enabled ? 1 : 0
  bucket                  = aws_s3_bucket.landing[0].id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "landing" {
  count  = var.enabled ? 1 : 0
  bucket = aws_s3_bucket.landing[0].id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "landing" {
  count  = var.enabled ? 1 : 0
  bucket = aws_s3_bucket.landing[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

output "database_secret_arn" {
  value = var.enabled ? aws_secretsmanager_secret.db[0].arn : null
}

output "landing_bucket_name" {
  value = var.enabled ? aws_s3_bucket.landing[0].bucket : null
}

output "rds_endpoint" {
  value = var.enabled ? aws_db_instance.postgres[0].address : null
}
