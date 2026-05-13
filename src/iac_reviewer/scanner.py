"""Scanner orchestration for Terraform review."""

from __future__ import annotations

from pathlib import Path

from .models import ScanResult
from .parser import TerraformResource, discover_tf_files, parse_resources
from .rules import evaluate

RULE_IDS = (
    "SEC-S3-PUBLIC",
    "SEC-SG-PUBLIC-INGRESS",
    "REL-RDS-BACKUP",
    "REL-RDS-MULTIAZ",
    "OPS-CW-LOGS",
    "OPS-CW-ALARMS",
    "OPS-TAGS",
    "COST-EC2-OVERSIZED",
    "COST-BUDGET",
    "PERF-SCALING",
    "PERF-CACHE",
)


def scan_paths(paths: list[Path]) -> ScanResult:
    """Scan Terraform files under paths and return Well-Architected findings."""

    tf_files = discover_tf_files(paths)
    resources: list[TerraformResource] = []
    for tf_file in tf_files:
        resources.extend(parse_resources(tf_file))
    findings = evaluate(resources)
    failed_rule_ids = {finding.rule_id for finding in findings}
    passed = tuple(rule_id for rule_id in RULE_IDS if rule_id not in failed_rule_ids)
    return ScanResult(scanned_files=tf_files, findings=findings, passed_checks=passed)
