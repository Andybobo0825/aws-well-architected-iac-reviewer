from __future__ import annotations

from pathlib import Path

from iac_reviewer.scanner import scan_paths


def write_tf(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "main.tf"
    path.write_text(content, encoding="utf-8")
    return path


def test_detects_required_well_architected_findings(tmp_path: Path) -> None:
    tf_file = write_tf(
        tmp_path,
        '''
resource "aws_s3_bucket" "public" {
  bucket = "demo-public"
  acl    = "public-read"
}

resource "aws_security_group" "ssh" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "db" {
  allocated_storage = 20
  engine            = "postgres"
}

resource "aws_instance" "big" {
  ami           = "ami-123"
  instance_type = "m5.24xlarge"
}
''',
    )

    result = scan_paths([tf_file])

    rule_ids = {finding.rule_id for finding in result.findings}
    assert "SEC-S3-PUBLIC" in rule_ids
    assert "SEC-SG-PUBLIC-INGRESS" in rule_ids
    assert "REL-RDS-BACKUP" in rule_ids
    assert "REL-RDS-MULTIAZ" in rule_ids
    assert "OPS-CW-LOGS" in rule_ids
    assert "OPS-CW-ALARMS" in rule_ids
    assert "OPS-TAGS" in rule_ids
    assert "COST-EC2-OVERSIZED" in rule_ids
    assert "COST-BUDGET" in rule_ids
    assert "PERF-SCALING" in rule_ids
    assert "PERF-CACHE" in rule_ids


def test_secure_fixture_has_no_findings(tmp_path: Path) -> None:
    tf_file = write_tf(
        tmp_path,
        '''
resource "aws_s3_bucket" "private" {
  bucket = "demo-private"
  tags = { Project = "iac-reviewer" }
}

resource "aws_s3_bucket_public_access_block" "private" {
  bucket                  = aws_s3_bucket.private.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
  tags = { Project = "iac-reviewer" }
}

resource "aws_security_group" "web" {
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  tags = { Project = "iac-reviewer" }
}

resource "aws_db_instance" "db" {
  allocated_storage       = 20
  engine                  = "postgres"
  backup_retention_period = 7
  multi_az                = true
  tags = { Project = "iac-reviewer" }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/demo/app"
  retention_in_days = 30
  tags = { Project = "iac-reviewer" }
}

resource "aws_cloudwatch_metric_alarm" "errors" {
  alarm_name          = "demo-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "Demo"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  tags = { Project = "iac-reviewer" }
}

resource "aws_budgets_budget" "monthly" {
  name         = "demo-budget"
  budget_type  = "COST"
  limit_amount = "25"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  tags = { Project = "iac-reviewer" }
}

resource "aws_autoscaling_group" "app" {
  min_size = 1
  max_size = 2
  tags = [{ key = "Project", value = "iac-reviewer", propagate_at_launch = true }]
}

resource "aws_elasticache_cluster" "cache" {
  cluster_id           = "demo-cache"
  engine               = "redis"
  node_type            = "cache.t4g.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  tags = { Project = "iac-reviewer" }
}
''',
    )

    result = scan_paths([tf_file])

    assert result.findings == ()


def test_discovers_nested_terraform_files(tmp_path: Path) -> None:
    nested = tmp_path / "examples" / "terraform"
    nested.mkdir(parents=True)
    (nested / "main.tf").write_text('resource "aws_budgets_budget" "monthly" { tags = { Project = "x" } }', encoding="utf-8")
    (nested / "notes.txt").write_text("ignored", encoding="utf-8")

    result = scan_paths([tmp_path])

    assert result.scanned_files == (nested / "main.tf",)
