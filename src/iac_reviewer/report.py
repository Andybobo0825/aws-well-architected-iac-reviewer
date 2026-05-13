"""Markdown report rendering."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone

from .models import Finding, ScanResult

PILLAR_ORDER = (
    "Security",
    "Reliability",
    "Operational Excellence",
    "Cost Optimization",
    "Performance Efficiency",
)
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def render_markdown(result: ScanResult) -> str:
    """Render a deterministic architecture-review.md report."""

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# AWS Well-Architected IaC Review",
        "",
        f"Generated: {generated_at}",
        "",
        "## Scope",
        "",
        f"- Terraform files scanned: {len(result.scanned_files)}",
        f"- Findings: {len(result.findings)}",
        "- Mode: static Terraform text analysis only; no AWS credentials, provider downloads, or Terraform apply.",
        "",
        "## Summary",
        "",
    ]
    if result.scanned_files:
        lines.append("Scanned files:")
        for path in result.scanned_files:
            lines.append(f"- `{path}`")
    else:
        lines.append("No Terraform files were found in the requested paths.")
    lines.append("")

    severity_counts = Counter(finding.severity for finding in result.findings)
    lines.extend(
        [
            "| Severity | Count |",
            "| --- | ---: |",
            f"| High | {severity_counts.get('high', 0)} |",
            f"| Medium | {severity_counts.get('medium', 0)} |",
            f"| Low | {severity_counts.get('low', 0)} |",
            "",
        ]
    )

    if result.passed_checks:
        lines.extend(["## Checks Without Findings", ""])
        for rule_id in result.passed_checks:
            lines.append(f"- `{rule_id}`")
        lines.append("")

    lines.extend(["## Findings", ""])
    if not result.findings:
        lines.extend(["No findings detected by the configured rule set.", ""])
    else:
        by_pillar: dict[str, list[Finding]] = defaultdict(list)
        for finding in result.findings:
            by_pillar[finding.pillar].append(finding)
        for pillar in PILLAR_ORDER:
            findings = by_pillar.get(pillar, [])
            if not findings:
                continue
            lines.extend([f"### {pillar}", ""])
            for finding in sorted(findings, key=lambda item: (SEVERITY_ORDER.get(item.severity, 99), item.rule_id, str(item.path), item.resource or "")):
                location = _location(finding)
                lines.extend(
                    [
                        f"#### {finding.title} (`{finding.rule_id}`)",
                        "",
                        f"- Severity: **{finding.severity.upper()}**",
                        f"- Location: {location}",
                        f"- Evidence: {finding.message}",
                        f"- Recommendation: {finding.recommendation}",
                        "",
                    ]
                )
    lines.extend(
        [
            "## Next Steps",
            "",
            "- Review high-severity findings before merging infrastructure changes.",
            "- Keep exceptions documented with workload context, owner, and expiry date.",
            "- Run this reviewer in pull requests alongside `terraform fmt` and unit tests.",
            "",
        ]
    )
    return "\n".join(lines)


def _location(finding: Finding) -> str:
    if finding.path and finding.resource:
        return f"`{finding.path}` resource `{finding.resource}`"
    if finding.path:
        return f"`{finding.path}`"
    return "repository-wide"
