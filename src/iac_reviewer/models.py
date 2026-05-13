"""Domain models for IaC review findings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    """A single Well-Architected review finding."""

    rule_id: str
    pillar: str
    severity: str
    title: str
    message: str
    path: Path | None = None
    resource: str | None = None
    recommendation: str = ""


@dataclass(frozen=True)
class ScanResult:
    """Aggregated result for a static Terraform scan."""

    scanned_files: tuple[Path, ...]
    findings: tuple[Finding, ...]
    passed_checks: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_findings(self) -> bool:
        return bool(self.findings)

    @property
    def finding_count_by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        return counts
