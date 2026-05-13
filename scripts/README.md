# Validation Scripts

`scripts/validate.sh` is the local validation entry point for this portfolio repository. It performs only static checks and never uses AWS credentials, `terraform plan`, or `terraform apply`.

Recommended local invocation:

```bash
scripts/validate.sh
```

Strict local validation, useful before publishing changes:

```bash
scripts/validate.sh --strict
```

The script runs shell syntax checks, Python compile/tests/lint when available, and Terraform formatting when Terraform is installed. In strict mode it also requires the expected project paths `src/`, `tests/`, and `examples/terraform/` to exist so incomplete scaffolds are caught early.
