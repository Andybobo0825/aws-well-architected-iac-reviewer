# Low-cost portfolio/demo fixture that should pass the static reviewer.
# Do not apply without normal Terraform/provider review.

locals {
  common_tags = {
    Project     = "aws-well-architected-iac-reviewer"
    Environment = "demo"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "private_assets" {
  bucket = "iac-reviewer-private-assets-demo"
  tags   = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "private_assets" {
  bucket                  = aws_s3_bucket.private_assets.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
  tags                    = local.common_tags
}

resource "aws_security_group" "app" {
  name        = "iac-reviewer-app"
  description = "HTTPS ingress from private demo CIDR only"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  tags = local.common_tags
}

resource "aws_db_instance" "orders" {
  identifier              = "iac-reviewer-orders"
  allocated_storage       = 20
  engine                  = "postgres"
  instance_class          = "db.t4g.micro"
  backup_retention_period = 7
  multi_az                = true
  username                = "demo"
  password                = "replace-me"
  tags                    = local.common_tags
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/demo/iac-reviewer/app"
  retention_in_days = 14
  tags              = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "app_errors" {
  alarm_name          = "iac-reviewer-demo-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "Demo/IaCReviewer"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  tags                = local.common_tags
}

resource "aws_budgets_budget" "monthly" {
  name         = "iac-reviewer-demo-budget"
  budget_type  = "COST"
  limit_amount = "25"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  tags         = local.common_tags
}

resource "aws_autoscaling_group" "app" {
  name     = "iac-reviewer-demo-app"
  min_size = 1
  max_size = 2

  tag {
    key                 = "Project"
    value               = "aws-well-architected-iac-reviewer"
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
