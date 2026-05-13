"""Command line interface for the AWS Well-Architected IaC reviewer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .report import render_markdown
from .scanner import scan_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Static AWS Well-Architected review for Terraform IaC.")
    parser.add_argument("paths", nargs="+", type=Path, help="Terraform files or directories to scan.")
    parser.add_argument("-o", "--output", type=Path, default=Path("architecture-review.md"), help="Markdown report path (default: architecture-review.md).")
    parser.add_argument("--fail-on", choices=("none", "low", "medium", "high"), default="none", help="Exit non-zero when findings at or above the selected severity exist.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    missing = [str(path) for path in args.paths if not path.exists()]
    if missing:
        print(f"error: path(s) not found: {', '.join(missing)}", file=sys.stderr)
        return 2

    result = scan_paths(args.paths)
    args.output.write_text(render_markdown(result), encoding="utf-8")
    print(f"Scanned {len(result.scanned_files)} Terraform file(s); wrote {args.output}; findings={len(result.findings)}")

    if _should_fail(result.finding_count_by_severity, args.fail_on):
        return 1
    return 0


def _should_fail(counts: dict[str, int], fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = {"low": 0, "medium": 1, "high": 2}[fail_on]
    order = {"low": 0, "medium": 1, "high": 2}
    return any(count and order[severity] >= threshold for severity, count in counts.items())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
