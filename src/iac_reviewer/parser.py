"""Small Terraform text parser used by the static rule engine.

This parser intentionally avoids Terraform execution, provider downloads, AWS
credentials, and heavyweight HCL dependencies. It extracts enough structure for
portfolio/demo Well-Architected checks while preserving deterministic behavior
for CI and unit tests.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_RESOURCE_START = re.compile(r'(?m)^\s*resource\s+"(?P<type>[^"]+)"\s+"(?P<name>[^"]+)"\s*\{')


@dataclass(frozen=True)
class TerraformResource:
    type: str
    name: str
    body: str
    path: Path

    @property
    def address(self) -> str:
        return f"{self.type}.{self.name}"


def strip_comments(text: str) -> str:
    """Remove Terraform comments while keeping strings good enough for scanning."""

    cleaned_lines: list[str] = []
    in_block = False
    for line in text.splitlines():
        current = line
        if in_block:
            end = current.find("*/")
            if end == -1:
                continue
            current = current[end + 2 :]
            in_block = False

        while "/*" in current:
            start = current.find("/*")
            end = current.find("*/", start + 2)
            if end == -1:
                current = current[:start]
                in_block = True
                break
            current = current[:start] + current[end + 2 :]

        # Terraform comments are commonly line-oriented. This deliberately does
        # not try to be a full lexer; tests cover the supported fixture style.
        for marker in ("#", "//"):
            marker_at = current.find(marker)
            if marker_at != -1:
                current = current[:marker_at]
        cleaned_lines.append(current)
    return "\n".join(cleaned_lines)


def discover_tf_files(paths: list[Path]) -> tuple[Path, ...]:
    """Return sorted Terraform files under the provided files/directories."""

    files: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix == ".tf":
            files.add(path)
        elif path.is_dir():
            files.update(candidate for candidate in path.rglob("*.tf") if candidate.is_file())
    return tuple(sorted(files))


def parse_resources(path: Path) -> tuple[TerraformResource, ...]:
    """Extract Terraform resource blocks from a .tf file."""

    text = strip_comments(path.read_text(encoding="utf-8"))
    resources: list[TerraformResource] = []
    for match in _RESOURCE_START.finditer(text):
        body_start = match.end()
        body_end = _find_matching_brace(text, body_start - 1)
        if body_end is None:
            continue
        body = text[body_start:body_end]
        resources.append(
            TerraformResource(
                type=match.group("type"),
                name=match.group("name"),
                body=body,
                path=path,
            )
        )
    return tuple(resources)


def _find_matching_brace(text: str, opening_brace_at: int) -> int | None:
    depth = 0
    in_string = False
    escaped = False
    for index in range(opening_brace_at, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None
