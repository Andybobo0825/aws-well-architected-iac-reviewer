from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _support  # noqa: F401
from iac_reviewer.cli import main


class CliTests(unittest.TestCase):
    def test_cli_writes_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            tmp_path = Path(raw_dir)
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

            self.assertEqual(0, exit_code)
            report = output.read_text(encoding="utf-8")
        self.assertIn("# AWS Well-Architected IaC Review", report)
        self.assertIn("SEC-S3-PUBLIC", report)
        self.assertNotIn("Output:", report)

    def test_cli_can_fail_on_high_findings(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            tmp_path = Path(raw_dir)
            fixture = tmp_path / "main.tf"
            fixture.write_text('resource "aws_s3_bucket" "public" { acl = "public-read" }', encoding="utf-8")
            output = tmp_path / "review.md"

            exit_code = main([str(fixture), "--output", str(output), "--fail-on", "high"])

        self.assertEqual(1, exit_code)

    def test_cli_returns_usage_error_for_missing_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw_dir:
            tmp_path = Path(raw_dir)
            output = tmp_path / "review.md"

            exit_code = main([str(tmp_path / "missing"), "--output", str(output)])

            self.assertEqual(2, exit_code)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
