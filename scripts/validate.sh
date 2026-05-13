#!/usr/bin/env bash
# Run local and CI validation for the AWS Well-Architected IaC Reviewer.
# This script is intentionally static-only: it never calls AWS APIs and never
# runs terraform apply/plan/validate against live providers.
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT=0
if [[ "${CI:-}" == "true" || "${CI:-}" == "1" ]]; then
  STRICT=1
fi

usage() {
  cat <<'USAGE'
Usage: scripts/validate.sh [--strict|--no-strict]

Checks performed:
  - shell syntax for validation scripts
  - Python compile check for src/ and tests/ when present
  - pytest when installed; otherwise unittest discovery fallback when tests/ exists
  - optional Python lint via ruff when installed
  - terraform fmt -check -recursive for examples/ and infra/ when Terraform is installed
  - optional GitHub Actions workflow lint via actionlint when installed

By default, strict mode is enabled in CI=true and disabled locally. Strict mode
fails when expected project paths (src, tests, examples/terraform) are missing.
The script does not use AWS credentials and does not run terraform apply.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict)
      STRICT=1
      shift
      ;;
    --no-strict)
      STRICT=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "ERROR: neither python3 nor python is available" >&2
    exit 1
  fi
fi

section() {
  printf '\n==> %s\n' "$1"
}

warn_or_fail() {
  local message="$1"
  if [[ "$STRICT" -eq 1 ]]; then
    echo "ERROR: $message" >&2
    exit 1
  fi
  echo "WARN: $message" >&2
}

existing_paths() {
  local path
  for path in "$@"; do
    [[ -e "$path" ]] && printf '%s\n' "$path"
  done
}

section "Validation mode"
if [[ "$STRICT" -eq 1 ]]; then
  echo "strict=true"
else
  echo "strict=false"
fi

section "Shell syntax"
shell_scripts=()
while IFS= read -r path; do
  shell_scripts+=("$path")
done < <(find scripts -type f -name '*.sh' | sort)
if [[ "${#shell_scripts[@]}" -eq 0 ]]; then
  warn_or_fail "no shell scripts found under scripts/"
else
  bash -n "${shell_scripts[@]}"
fi

section "Python compile"
python_compile_paths=()
while IFS= read -r path; do
  python_compile_paths+=("$path")
done < <(existing_paths src tests)
if [[ "${#python_compile_paths[@]}" -eq 0 ]]; then
  warn_or_fail "neither src/ nor tests/ exists for compileall"
else
  "$PYTHON_BIN" -m compileall "${python_compile_paths[@]}"
fi

section "Python tests"
if [[ -d tests ]]; then
  if "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
    "$PYTHON_BIN" -m pytest
  else
    echo "pytest is not installed; falling back to unittest discovery"
    "$PYTHON_BIN" -m unittest discover -s tests
  fi
else
  warn_or_fail "tests/ does not exist"
fi

section "Python lint"
python_lint_paths=()
while IFS= read -r path; do
  python_lint_paths+=("$path")
done < <(existing_paths src tests)
if [[ "${#python_lint_paths[@]}" -eq 0 ]]; then
  warn_or_fail "neither src/ nor tests/ exists for Python lint"
elif "$PYTHON_BIN" -m ruff --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m ruff check "${python_lint_paths[@]}"
else
  echo "ruff is not installed; compileall already provided Python syntax coverage"
fi

section "Terraform formatting"
terraform_paths=()
while IFS= read -r path; do
  terraform_paths+=("$path")
done < <(existing_paths examples infra)
if [[ "${#terraform_paths[@]}" -eq 0 ]]; then
  warn_or_fail "neither examples/ nor infra/ exists for terraform fmt"
elif command -v terraform >/dev/null 2>&1; then
  terraform fmt -check -recursive "${terraform_paths[@]}"
else
  echo "terraform is not installed; skipping terraform fmt check"
fi

section "GitHub Actions lint"
if [[ -d .github/workflows ]]; then
  workflow_files=()
  while IFS= read -r path; do
    workflow_files+=("$path")
  done < <(find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)
  if [[ "${#workflow_files[@]}" -eq 0 ]]; then
    warn_or_fail ".github/workflows exists but contains no YAML workflows"
  elif command -v actionlint >/dev/null 2>&1; then
    actionlint "${workflow_files[@]}"
  else
    echo "actionlint is not installed; skipping workflow lint"
  fi
else
  echo ".github/workflows does not exist yet; skipping workflow lint"
fi

section "Validation complete"
echo "PASS"
