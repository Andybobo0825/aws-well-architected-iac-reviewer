terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "Demo AWS region; static scanner fixture only, do not apply."
  type        = string
  default     = "ap-northeast-1"
}

locals {
  common_tags = {
    Project     = "aws-well-architected-iac-reviewer"
    Environment = "demo"
    Owner       = "portfolio"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "private_artifacts" {
  bucket = "iac-reviewer-private-artifacts-demo"
  tags   = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "private_artifacts" {
  bucket                  = aws_s3_bucket.private_artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_security_group" "app" {
  name        = "iac-reviewer-private-app"
  description = "Restricts ingress to private demo network space."

  ingress {
    description = "Private HTTPS only"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_db_instance" "orders" {
  identifier              = "iac-reviewer-orders-demo"
  allocated_storage       = 20
  engine                  = "postgres"
  instance_class          = "db.t3.micro"
  username                = "demo"
  password                = "not-for-apply-demo-only"
  backup_retention_period = 7
  multi_az                = true
  skip_final_snapshot     = true
  tags                    = local.common_tags
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/demo/iac-reviewer/app"
  retention_in_days = 30
  tags              = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "errors" {
  alarm_name          = "iac-reviewer-demo-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "IacReviewer/Demo"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Demo alarm fixture for operational excellence coverage."
  tags                = local.common_tags
}

resource "aws_budgets_budget" "monthly" {
  name         = "iac-reviewer-demo-monthly"
  budget_type  = "COST"
  limit_amount = "25"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  tags         = local.common_tags
}

resource "aws_launch_template" "app" {
  name_prefix   = "iac-reviewer-demo-"
  image_id      = "ami-1234567890abcdef0"
  instance_type = "t4g.micro"

  tag_specifications {
    resource_type = "instance"
    tags          = local.common_tags
  }

  tags = local.common_tags
}

resource "aws_autoscaling_group" "app" {
  name                = "iac-reviewer-demo-app"
  min_size            = 1
  max_size            = 2
  desired_capacity    = 1
  vpc_zone_identifier = ["subnet-0123456789abcdef0"]

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Project"
    value               = local.common_tags.Project
    propagate_at_launch = true
  }
}

resource "aws_elasticache_cluster" "cache" {
  cluster_id           = "iac-reviewer-demo-cache"
  engine               = "redis"
  node_type            = "cache.t4g.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  tags                 = local.common_tags
}
