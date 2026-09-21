# Production observability — CloudWatch alarms and AWS Budgets.
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

variable "alb_arn_suffix" {
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

variable "tags" {
  type    = map(string)
  default = {}
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  count               = var.enabled && var.alb_arn_suffix != "" ? 1 : 0
  alarm_name          = "${var.name_prefix}-alb-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "ALB target 5xx elevated"
  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }
  tags = var.tags
}

resource "aws_budgets_budget" "monthly" {
  count        = var.enabled ? 1 : 0
  name         = "${var.name_prefix}-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.budget_limit_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  dynamic "notification" {
    for_each = var.budget_notification_email != "" ? [1] : []
    content {
      comparison_operator        = "GREATER_THAN"
      threshold                  = 80
      threshold_type             = "PERCENTAGE"
      notification_type          = "ACTUAL"
      subscriber_email_addresses = [var.budget_notification_email]
    }
  }
}
