# AWS Well-Architected IaC Reviewer

A portfolio-ready static reviewer for Terraform projects. It scans Infrastructure as Code before deployment and writes an AWS Well-Architected-style Markdown report named `architecture-review.md`.

The project is intentionally local and safe for demos: it does **not** call AWS APIs, require AWS credentials, run `terraform apply`, or create cloud resources.

## Why this project exists

Cloud architecture reviews often happen late, after Terraform is already close to production. This repository turns a focused subset of AWS Well-Architected review questions into automated pull-request feedback so common risks are visible earlier.

It demonstrates:

- AWS architecture review thinking across the five Well-Architected pillars.
- Practical Terraform static analysis without cloud-side side effects.
- Markdown reporting that can be reviewed in GitHub pull requests.
- CI automation suitable for a Cloud Solution Architect / DevOps portfolio.

## Review coverage

| Pillar | Check family | Examples of signals |
| --- | --- | --- |
| Security | Public exposure | Public S3 access, permissive Security Group ingress such as `0.0.0.0/0` |
| Reliability | Data resilience | RDS backup retention and Multi-AZ configuration signals |
| Operational Excellence | Operability | CloudWatch logs, alarms, and required tags |
| Cost Optimization | Cost guardrails | Oversized compute and missing AWS Budget coverage |
| Performance Efficiency | Scaling and caching | Auto Scaling and cache design hints |

Rules are intentionally transparent and conservative. Findings should be treated as review prompts, not as a replacement for a complete AWS Well-Architected Review.

## Expected repository layout

```text
.
├── src/iac_reviewer/             # Python CLI and rule engine
├── tests/                        # Unit and fixture tests
├── examples/terraform/           # Secure and insecure Terraform fixtures
├── docs/ARCHITECTURE.md          # System design and data flow
├── docs/RULES.md                 # Rule catalog and fixture mapping
├── docs/ROADMAP_ALIGNMENT.md     # Portfolio roadmap traceability
├── infra/terraform-intake.md     # Intake template for reviewing Terraform projects
└── .github/workflows/iac-review.yml
```

## Quick start

> The exact package entrypoint is implemented by the Python CLI slice. The commands below describe the intended local workflow.

```bash
python -m compileall src tests
python -m pytest
python -m iac_reviewer examples/terraform/insecure --output architecture-review.md
```

If Terraform is installed, validate formatting for repository fixtures:

```bash
terraform fmt -check -recursive examples infra
```

## GitHub Actions workflow

The included workflow runs on pull requests and pushes. It is designed for parallel repository construction and final CI use:

1. Set up Python.
2. Install project/test dependencies when dependency files are present.
3. Compile Python sources and tests.
4. Run pytest when tests exist.
5. Run Terraform formatting checks when Terraform files and the Terraform CLI are available.
6. Run the reviewer against Terraform examples when the CLI package and fixtures are present.
7. Upload `architecture-review.md` as a workflow artifact when generated.

## Safety boundaries

- Static file scanning only.
- No AWS credentials are required or requested.
- No `terraform init`, `terraform plan`, or `terraform apply` is required for the reviewer workflow.
- Example Terraform is for detection coverage and portfolio discussion, not production deployment.

## Example report shape

`architecture-review.md` should include:

- Review summary and scanned path.
- Risk level for each finding.
- Well-Architected pillar mapping.
- File/resource evidence.
- Suggested remediation.
- A short note for assumptions and review limitations.

## Roadmap alignment

This repository implements the roadmap project “AWS Well-Architected IaC Reviewer”: a Terraform-focused scanner that converts AWS architecture best practices into automated review feedback and produces a Markdown architecture review report.
