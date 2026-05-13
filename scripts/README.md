# Validation Scripts

`scripts/validate.sh` is the single local/CI validation entry point for this
portfolio repository. It performs only static checks and never uses AWS
credentials or `terraform apply`.

Recommended CI invocation:

```bash
CI=true scripts/validate.sh --strict
```

Useful local bootstrap invocation while parallel workers are still creating the
repo structure:

```bash
scripts/validate.sh --no-strict
```

The script runs Python compile/tests/lint, Terraform formatting when Terraform
is installed, shell syntax checks, and optional GitHub Actions linting when
`actionlint` is available.
