# Production networking — VPC, subnets, NAT, security groups.
# Paid resources only when var.enabled = true.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "enabled" {
  type        = bool
  description = "When false, no AWS networking resources are created."
}

variable "name_prefix" {
  type = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "azs" {
  type    = list(string)
  default = []
}

variable "tags" {
  type    = map(string)
  default = {}
}

data "aws_availability_zones" "available" {
  count = var.enabled ? 1 : 0
  state = "available"
}

locals {
  azs = length(var.azs) > 0 ? var.azs : (
    var.enabled ? slice(data.aws_availability_zones.available[0].names, 0, 2) : []
  )
  public_cidrs  = [cidrsubnet(var.vpc_cidr, 4, 0), cidrsubnet(var.vpc_cidr, 4, 1)]
  private_cidrs = [cidrsubnet(var.vpc_cidr, 4, 2), cidrsubnet(var.vpc_cidr, 4, 3)]
}

resource "aws_vpc" "this" {
  count                = var.enabled ? 1 : 0
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = merge(var.tags, { Name = "${var.name_prefix}-vpc" })
}

resource "aws_internet_gateway" "this" {
  count  = var.enabled ? 1 : 0
  vpc_id = aws_vpc.this[0].id
  tags   = merge(var.tags, { Name = "${var.name_prefix}-igw" })
}

resource "aws_subnet" "public" {
  count                   = var.enabled ? length(local.azs) : 0
  vpc_id                  = aws_vpc.this[0].id
  cidr_block              = local.public_cidrs[count.index]
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true
  tags                    = merge(var.tags, { Name = "${var.name_prefix}-public-${count.index}" })
}

resource "aws_subnet" "private" {
  count             = var.enabled ? length(local.azs) : 0
  vpc_id            = aws_vpc.this[0].id
  cidr_block        = local.private_cidrs[count.index]
  availability_zone = local.azs[count.index]
  tags              = merge(var.tags, { Name = "${var.name_prefix}-private-${count.index}" })
}

resource "aws_eip" "nat" {
  count  = var.enabled ? 1 : 0
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.name_prefix}-nat-eip" })
}

resource "aws_nat_gateway" "this" {
  count         = var.enabled ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
  tags          = merge(var.tags, { Name = "${var.name_prefix}-nat" })
  depends_on    = [aws_internet_gateway.this]
}

resource "aws_route_table" "public" {
  count  = var.enabled ? 1 : 0
  vpc_id = aws_vpc.this[0].id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this[0].id
  }
  tags = merge(var.tags, { Name = "${var.name_prefix}-public-rt" })
}

resource "aws_route_table_association" "public" {
  count          = var.enabled ? length(aws_subnet.public) : 0
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

resource "aws_route_table" "private" {
  count  = var.enabled ? 1 : 0
  vpc_id = aws_vpc.this[0].id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this[0].id
  }
  tags = merge(var.tags, { Name = "${var.name_prefix}-private-rt" })
}

resource "aws_route_table_association" "private" {
  count          = var.enabled ? length(aws_subnet.private) : 0
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}

resource "aws_security_group" "alb" {
  count       = var.enabled ? 1 : 0
  name        = "${var.name_prefix}-alb"
  description = "ALB ingress"
  vpc_id      = aws_vpc.this[0].id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(var.tags, { Name = "${var.name_prefix}-alb-sg" })
}

resource "aws_security_group" "ecs" {
  count       = var.enabled ? 1 : 0
  name        = "${var.name_prefix}-ecs"
  description = "ECS tasks"
  vpc_id      = aws_vpc.this[0].id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb[0].id]
  }
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb[0].id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(var.tags, { Name = "${var.name_prefix}-ecs-sg" })
}

resource "aws_security_group" "rds" {
  count       = var.enabled ? 1 : 0
  name        = "${var.name_prefix}-rds"
  description = "RDS Postgres from ECS only"
  vpc_id      = aws_vpc.this[0].id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs[0].id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(var.tags, { Name = "${var.name_prefix}-rds-sg" })
}

output "vpc_id" {
  value = var.enabled ? aws_vpc.this[0].id : null
}

output "public_subnet_ids" {
  value = var.enabled ? aws_subnet.public[*].id : []
}

output "private_subnet_ids" {
  value = var.enabled ? aws_subnet.private[*].id : []
}

output "alb_security_group_id" {
  value = var.enabled ? aws_security_group.alb[0].id : null
}

output "ecs_security_group_id" {
  value = var.enabled ? aws_security_group.ecs[0].id : null
}

output "rds_security_group_id" {
  value = var.enabled ? aws_security_group.rds[0].id : null
}
