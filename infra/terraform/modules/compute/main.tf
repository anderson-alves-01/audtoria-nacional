# Production compute — ECR, ECS Fargate, ALB.
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
  type = bool
}

variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "alb_security_group_id" {
  type = string
}

variable "ecs_security_group_id" {
  type = string
}

variable "database_secret_arn" {
  type = string
}

variable "landing_bucket_name" {
  type = string
}

variable "acm_certificate_arn" {
  type        = string
  default     = ""
  description = "Optional ACM cert for HTTPS. Empty keeps HTTP-only listener for bootstrap."
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

variable "tags" {
  type    = map(string)
  default = {}
}

resource "aws_ecr_repository" "api" {
  count                = var.enabled ? 1 : 0
  name                 = "${var.name_prefix}-api"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = var.tags
}

resource "aws_ecr_repository" "web" {
  count                = var.enabled ? 1 : 0
  name                 = "${var.name_prefix}-web"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = var.tags
}

resource "aws_ecr_repository" "worker" {
  count                = var.enabled ? 1 : 0
  name                 = "${var.name_prefix}-worker"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "api" {
  count             = var.enabled ? 1 : 0
  name              = "/ecs/${var.name_prefix}/api"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "web" {
  count             = var.enabled ? 1 : 0
  name              = "/ecs/${var.name_prefix}/web"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "worker" {
  count             = var.enabled ? 1 : 0
  name              = "/ecs/${var.name_prefix}/worker"
  retention_in_days = 30
  tags              = var.tags
}

resource "aws_iam_role" "ecs_execution" {
  count = var.enabled ? 1 : 0
  name  = "${var.name_prefix}-ecs-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  count      = var.enabled ? 1 : 0
  role       = aws_iam_role.ecs_execution[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_secrets" {
  count = var.enabled ? 1 : 0
  name  = "${var.name_prefix}-ecs-secrets"
  role  = aws_iam_role.ecs_execution[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [var.database_secret_arn]
    }]
  })
}

resource "aws_iam_role" "ecs_task" {
  count = var.enabled ? 1 : 0
  name  = "${var.name_prefix}-ecs-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "ecs_task_s3" {
  count = var.enabled ? 1 : 0
  name  = "${var.name_prefix}-ecs-s3"
  role  = aws_iam_role.ecs_task[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource = [
        "arn:aws:s3:::${var.landing_bucket_name}",
        "arn:aws:s3:::${var.landing_bucket_name}/*"
      ]
    }]
  })
}

resource "aws_ecs_cluster" "this" {
  count = var.enabled ? 1 : 0
  name  = var.name_prefix
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = var.tags
}

resource "aws_lb" "this" {
  count              = var.enabled ? 1 : 0
  name               = "${var.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids
  tags               = var.tags
}

resource "aws_lb_target_group" "api" {
  count       = var.enabled ? 1 : 0
  name        = "${var.name_prefix}-api"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
  tags = var.tags
}

resource "aws_lb_target_group" "web" {
  count       = var.enabled ? 1 : 0
  name        = "${var.name_prefix}-web"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200-399"
  }
  tags = var.tags
}

resource "aws_lb_listener" "http" {
  count             = var.enabled ? 1 : 0
  load_balancer_arn = aws_lb.this[0].arn
  port              = 80
  protocol          = "HTTP"

  dynamic "default_action" {
    for_each = var.acm_certificate_arn == "" ? [1] : []
    content {
      type             = "forward"
      target_group_arn = aws_lb_target_group.web[0].arn
    }
  }

  dynamic "default_action" {
    for_each = var.acm_certificate_arn != "" ? [1] : []
    content {
      type = "redirect"
      redirect {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = var.enabled && var.acm_certificate_arn != "" ? 1 : 0
  load_balancer_arn = aws_lb.this[0].arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web[0].arn
  }
}

resource "aws_lb_listener_rule" "api" {
  count        = var.enabled ? 1 : 0
  listener_arn = var.acm_certificate_arn != "" ? aws_lb_listener.https[0].arn : aws_lb_listener.http[0].arn
  priority     = 10
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api[0].arn
  }
  condition {
    path_pattern { values = ["/v1/*", "/health", "/docs", "/openapi.json"] }
  }
}

locals {
  api_image    = var.api_image != "" ? var.api_image : (var.enabled ? "${aws_ecr_repository.api[0].repository_url}:pending" : "")
  web_image    = var.web_image != "" ? var.web_image : (var.enabled ? "${aws_ecr_repository.web[0].repository_url}:pending" : "")
  worker_image = var.worker_image != "" ? var.worker_image : (var.enabled ? "${aws_ecr_repository.worker[0].repository_url}:pending" : "")
}

resource "aws_ecs_task_definition" "api" {
  count                    = var.enabled ? 1 : 0
  family                   = "${var.name_prefix}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution[0].arn
  task_role_arn            = aws_iam_role.ecs_task[0].arn
  container_definitions = jsonencode([{
    name         = "api"
    image        = local.api_image
    essential    = true
    portMappings = [{ containerPort = 8080, protocol = "tcp" }]
    secrets = [{
      name      = "DATABASE_URL"
      valueFrom = "${var.database_secret_arn}:database_url::"
    }]
    environment = [
      { name = "SIRTA_ENV", value = "prod" },
      { name = "S3_BUCKET", value = var.landing_bucket_name }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.api[0].name
        awslogs-region        = data.aws_region.current[0].name
        awslogs-stream-prefix = "api"
      }
    }
  }])
  tags = var.tags
}

resource "aws_ecs_task_definition" "web" {
  count                    = var.enabled ? 1 : 0
  family                   = "${var.name_prefix}-web"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution[0].arn
  task_role_arn            = aws_iam_role.ecs_task[0].arn
  container_definitions = jsonencode([{
    name         = "web"
    image        = local.web_image
    essential    = true
    portMappings = [{ containerPort = 80, protocol = "tcp" }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.web[0].name
        awslogs-region        = data.aws_region.current[0].name
        awslogs-stream-prefix = "web"
      }
    }
  }])
  tags = var.tags
}

resource "aws_ecs_task_definition" "worker" {
  count                    = var.enabled ? 1 : 0
  family                   = "${var.name_prefix}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution[0].arn
  task_role_arn            = aws_iam_role.ecs_task[0].arn
  container_definitions = jsonencode([{
    name      = "worker"
    image     = local.worker_image
    essential = true
    secrets = [{
      name      = "DATABASE_URL"
      valueFrom = "${var.database_secret_arn}:database_url::"
    }]
    environment = [
      { name = "SIRTA_ENV", value = "prod" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.worker[0].name
        awslogs-region        = data.aws_region.current[0].name
        awslogs-stream-prefix = "worker"
      }
    }
  }])
  tags = var.tags
}

data "aws_region" "current" {
  count = var.enabled ? 1 : 0
}

resource "aws_ecs_service" "api" {
  count           = var.enabled ? 1 : 0
  name            = "${var.name_prefix}-api"
  cluster         = aws_ecs_cluster.this[0].id
  task_definition = aws_ecs_task_definition.api[0].arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.api[0].arn
    container_name   = "api"
    container_port   = 8080
  }
  depends_on = [aws_lb_listener.http]
  tags       = var.tags
}

resource "aws_ecs_service" "web" {
  count           = var.enabled ? 1 : 0
  name            = "${var.name_prefix}-web"
  cluster         = aws_ecs_cluster.this[0].id
  task_definition = aws_ecs_task_definition.web[0].arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.web[0].arn
    container_name   = "web"
    container_port   = 80
  }
  depends_on = [aws_lb_listener.http]
  tags       = var.tags
}

resource "aws_ecs_service" "worker" {
  count           = var.enabled ? 1 : 0
  name            = "${var.name_prefix}-worker"
  cluster         = aws_ecs_cluster.this[0].id
  task_definition = aws_ecs_task_definition.worker[0].arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }
  tags = var.tags
}

output "alb_dns_name" {
  value = var.enabled ? aws_lb.this[0].dns_name : null
}

output "ecr_api_url" {
  value = var.enabled ? aws_ecr_repository.api[0].repository_url : null
}

output "ecr_web_url" {
  value = var.enabled ? aws_ecr_repository.web[0].repository_url : null
}

output "ecr_worker_url" {
  value = var.enabled ? aws_ecr_repository.worker[0].repository_url : null
}

output "ecs_cluster_name" {
  value = var.enabled ? aws_ecs_cluster.this[0].name : null
}
