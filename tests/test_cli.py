from __future__ import annotations

from pathlib import Path

from iac_reviewer.cli import main


def test_cli_writes_markdown_report(tmp_path: Path) -> None:
    fixture = tmp_path / "main.tf"
    fixture.write_text(
        '''
resource "aws_s3_bucket" "public" {
  acl = "public-read"
}
''',
        encoding="utf-8",
    )
    output = tmp_path / "architecture-review.md"

    exit_code = main([str(fixture), "--output", str(output)])

    assert exit_code == 0
    report = output.read_text(encoding="utf-8")
    assert "# AWS Well-Architected IaC Review" in report
    assert "SEC-S3-PUBLIC" in report
    assert "architecture-review.md" not in report  # output path is not self-referential noise


def test_cli_can_fail_on_high_findings(tmp_path: Path) -> None:
    fixture = tmp_path / "main.tf"
    fixture.write_text('resource "aws_s3_bucket" "public" { acl = "public-read" }', encoding="utf-8")
    output = tmp_path / "review.md"

    assert main([str(fixture), "--output", str(output), "--fail-on", "high"]) == 1


def test_cli_returns_usage_error_for_missing_path(tmp_path: Path) -> None:
    output = tmp_path / "review.md"

    assert main([str(tmp_path / "missing"), "--output", str(output)]) == 2
    assert not output.exists()
