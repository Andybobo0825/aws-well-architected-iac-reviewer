"""Well-Architected rule checks for static Terraform review."""

from __future__ import annotations

import re
from collections.abc import Iterable

from .models import Finding
from .parser import TerraformResource

PUBLIC_CIDRS = ("0.0.0.0/0", "::/0")
OVERSIZED_INSTANCE_CLASSES = (
    "metal",
    "8xlarge",
    "9xlarge",
    "10xlarge",
    "12xlarge",
    "16xlarge",
    "18xlarge",
    "24xlarge",
    "32xlarge",
    "48xlarge",
    "56xlarge",
    "112xlarge",
)


def evaluate(resources: Iterable[TerraformResource]) -> tuple[Finding, ...]:
    """Evaluate all rule families against parsed Terraform resources."""

    resource_tuple = tuple(resources)
    findings: list[Finding] = []
    findings.extend(_check_public_s3(resource_tuple))
    findings.extend(_check_security_groups(resource_tuple))
    findings.extend(_check_rds_reliability(resource_tuple))
    findings.extend(_check_observability_and_tags(resource_tuple))
    findings.extend(_check_cost(resource_tuple))
    findings.extend(_check_performance(resource_tuple))
    return tuple(findings)


def _check_public_s3(resources: tuple[TerraformResource, ...]) -> list[Finding]:
    findings: list[Finding] = []
    for resource in resources:
        compact = _compact(resource.body)
        if resource.type == "aws_s3_bucket" and re.search(r'\bacl\s*=\s*"?public-read', resource.body):
            findings.append(_finding("SEC-S3-PUBLIC", "Security", "high", "Public S3 bucket ACL", "S3 bucket ACL allows public access.", resource, "Keep S3 buckets private and use explicit CloudFront/OAC or signed URL patterns when public distribution is required."))
        if resource.type == "aws_s3_bucket_public_access_block":
            for field in ("block_public_acls", "block_public_policy", "ignore_public_acls", "restrict_public_buckets"):
                if re.search(rf'\b{field}\s*=\s*false\b', compact):
                    findings.append(_finding("SEC-S3-PUBLIC", "Security", "high", "S3 public access block disabled", f"{field} is disabled, which weakens S3 public access protection.", resource, "Set all S3 public access block controls to true unless a documented exception exists."))
                    break
        if resource.type == "aws_s3_bucket_policy" and '"*"' in resource.body and re.search(r's3:(GetObject|PutObject|\*)', resource.body, re.IGNORECASE):
            findings.append(_finding("SEC-S3-PUBLIC", "Security", "high", "S3 bucket policy grants public principal", "Bucket policy grants S3 actions to Principal '*'.", resource, "Restrict principals to specific AWS identities and avoid anonymous S3 access."))
    return findings


def _check_security_groups(resources: tuple[TerraformResource, ...]) -> list[Finding]:
    findings: list[Finding] = []
    for resource in resources:
        if resource.type not in {"aws_security_group", "aws_security_group_rule", "aws_vpc_security_group_ingress_rule"}:
            continue
        body = resource.body
        if not any(cidr in body for cidr in PUBLIC_CIDRS):
            continue
        ingress_like = resource.type != "aws_security_group_rule" or re.search(r'\btype\s*=\s*"ingress"', body)
        if not ingress_like:
            continue
        if _allows_all_ports(body) or _has_risky_public_port(body):
            findings.append(_finding("SEC-SG-PUBLIC-INGRESS", "Security", "high", "Permissive public ingress", "Security group ingress is open to the internet on all or sensitive ports.", resource, "Limit ingress CIDRs, prefer private connectivity, and document required public endpoints."))
    return findings


def _check_rds_reliability(resources: tuple[TerraformResource, ...]) -> list[Finding]:
    findings: list[Finding] = []
    for resource in resources:
        if resource.type not in {"aws_db_instance", "aws_rds_cluster"}:
            continue
        body = resource.body
        backup_match = re.search(r'\bbackup_retention_period\s*=\s*(\d+)', body)
        if not backup_match or int(backup_match.group(1)) < 1:
            findings.append(_finding("REL-RDS-BACKUP", "Reliability", "medium", "RDS backup retention missing", "RDS resources should retain automated backups for recovery objectives.", resource, "Set backup_retention_period to at least 1 day for portfolio/demo and align production values to RPO/RTO."))
        if resource.type == "aws_db_instance" and not re.search(r'\bmulti_az\s*=\s*true\b', _compact(body)):
            findings.append(_finding("REL-RDS-MULTIAZ", "Reliability", "medium", "RDS Multi-AZ signal missing", "RDS instance does not explicitly enable Multi-AZ resilience.", resource, "Use multi_az = true for production-like databases or document why a demo workload avoids the cost."))
    return findings


def _check_observability_and_tags(resources: tuple[TerraformResource, ...]) -> list[Finding]:
    findings: list[Finding] = []
    if resources and not any(resource.type == "aws_cloudwatch_log_group" for resource in resources):
        findings.append(_global_finding("OPS-CW-LOGS", "Operational Excellence", "medium", "CloudWatch log group missing", "No aws_cloudwatch_log_group resource was found.", "Add log groups with retention settings for workloads that emit logs."))
    if resources and not any(resource.type == "aws_cloudwatch_metric_alarm" for resource in resources):
        findings.append(_global_finding("OPS-CW-ALARMS", "Operational Excellence", "medium", "CloudWatch alarm missing", "No aws_cloudwatch_metric_alarm resource was found.", "Add alarms for critical health, latency, error, and cost signals."))
    for resource in resources:
        if resource.type.startswith("aws_") and resource.type not in {"aws_iam_policy_document"} and not re.search(r'\btags\s*=\s*\{', resource.body):
            findings.append(_finding("OPS-TAGS", "Operational Excellence", "low", "AWS resource missing tags", "AWS resource has no tags block for ownership, environment, or cost allocation.", resource, "Add common tags such as Project, Environment, Owner, and ManagedBy."))
    return findings


def _check_cost(resources: tuple[TerraformResource, ...]) -> list[Finding]:
    findings: list[Finding] = []
    for resource in resources:
        if resource.type == "aws_instance":
            instance_type = _string_attr(resource.body, "instance_type")
            if instance_type and any(instance_type.endswith(f".{size}") or f".{size}." in instance_type for size in OVERSIZED_INSTANCE_CLASSES):
                findings.append(_finding("COST-EC2-OVERSIZED", "Cost Optimization", "medium", "Oversized EC2 instance", f"EC2 instance type {instance_type} is large for a portfolio/demo workload.", resource, "Use smaller burstable or Graviton instance classes for demos unless load testing justifies capacity."))
    if resources and not any(resource.type == "aws_budgets_budget" for resource in resources):
        findings.append(_global_finding("COST-BUDGET", "Cost Optimization", "medium", "Budget coverage missing", "No aws_budgets_budget resource was found.", "Add a monthly budget with notifications for demo environments."))
    return findings


def _check_performance(resources: tuple[TerraformResource, ...]) -> list[Finding]:
    findings: list[Finding] = []
    has_compute = any(resource.type in {"aws_instance", "aws_launch_template", "aws_lb"} for resource in resources)
    has_scaling = any(resource.type in {"aws_autoscaling_group", "aws_appautoscaling_target", "aws_appautoscaling_policy"} for resource in resources)
    has_cache = any(resource.type.startswith("aws_elasticache") or resource.type in {"aws_dynamodb_table"} for resource in resources)
    if has_compute and not has_scaling:
        findings.append(_global_finding("PERF-SCALING", "Performance Efficiency", "low", "Auto Scaling signal missing", "Compute resources exist without Auto Scaling configuration.", "Use Auto Scaling groups, app autoscaling targets, or document why fixed capacity is sufficient."))
    if has_compute and not has_cache:
        findings.append(_global_finding("PERF-CACHE", "Performance Efficiency", "low", "Cache/read optimization signal missing", "Compute resources exist without an obvious cache or managed read-optimization service.", "Consider ElastiCache, DynamoDB, CDN, or query/cache design notes for read-heavy workloads."))
    return findings


def _finding(rule_id: str, pillar: str, severity: str, title: str, message: str, resource: TerraformResource, recommendation: str) -> Finding:
    return Finding(rule_id=rule_id, pillar=pillar, severity=severity, title=title, message=message, path=resource.path, resource=resource.address, recommendation=recommendation)


def _global_finding(rule_id: str, pillar: str, severity: str, title: str, message: str, recommendation: str) -> Finding:
    return Finding(rule_id=rule_id, pillar=pillar, severity=severity, title=title, message=message, recommendation=recommendation)


def _compact(text: str) -> str:
    return re.sub(r'\s+', ' ', text).lower()


def _string_attr(body: str, name: str) -> str | None:
    match = re.search(rf'\b{name}\s*=\s*"([^"]+)"', body)
    return match.group(1) if match else None


def _allows_all_ports(body: str) -> bool:
    compact = _compact(body)
    return bool(re.search(r'from_port\s*=\s*0\b', compact) and re.search(r'to_port\s*=\s*0\b', compact) and re.search(r'protocol\s*=\s*"?-?1"?', compact))


def _has_risky_public_port(body: str) -> bool:
    risky_ports = {22, 3389, 3306, 5432, 6379, 9200, 9300}
    from_match = re.search(r'\bfrom_port\s*=\s*(\d+)', body)
    to_match = re.search(r'\bto_port\s*=\s*(\d+)', body)
    if not from_match or not to_match:
        return False
    start = int(from_match.group(1))
    end = int(to_match.group(1))
    return any(start <= port <= end for port in risky_ports)
