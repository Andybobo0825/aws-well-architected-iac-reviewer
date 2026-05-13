# Context Snapshot: AWS Well-Architected IaC Reviewer

## Task statement
Build the roadmap's second portfolio project: `aws-well-architected-iac-reviewer`, using parallel OMX team workers. The project should scan Terraform/IaC and produce an AWS Well-Architected-style Markdown review report. It must include architecture, Terraform examples, tests, CI, and GitHub repository publication under `andybobo0825` when credentials/available tooling allow.

## Desired outcome
- A new local repository at `aws-well-architected-iac-reviewer`.
- Terraform-focused Well-Architected reviewer implementation and docs.
- Roadmap-aligned checks: Security, Reliability, Operational Excellence, Cost Optimization, Performance Efficiency.
- Markdown report output: `architecture-review.md`.
- GitHub Actions integration for PR/repo automation.
- Validation evidence: unit tests, Python compile checks, Terraform fmt/validate where possible.

## Known facts/evidence
- `cloud-sa-devops-portfolio-roadmap.md` lines 96-154 define project 2.
- Repo name suggested by roadmap: `aws-well-architected-iac-reviewer`.
- Reference: `aws-incident-response-observability-lab/cloud_deploy_skill/skill/terraform-cloud-planner/references/aws-question-bank.md`.
- Planner defaults: portfolio/demo, Taiwan/HK region defaults `ap-east-1` or `ap-northeast-1`, avoid NAT Gateway/Multi-AZ RDS/WAF/Route53/TLS unless requested.
- `gh` CLI is not installed in this environment; GitHub repo creation must use another authenticated method or be reported as blocked.

## Constraints
- Do not apply Terraform or use AWS credentials.
- Keep cloud resources demo/portfolio oriented and low-cost.
- No workers may remain idle with failing tests; each worker should verify its slice, commit, report, and end.
- Preserve existing language boundaries in existing projects; this is a new repo, so Python CLI + Terraform examples are acceptable.
- Commit messages must follow Lore protocol if committing.

## Assumptions
- Environment purpose: portfolio/demo.
- Region default: `ap-northeast-1` for examples unless overridden.
- Runtime: local CLI + GitHub Actions, not deployed cloud service.
- Scope: static Terraform HCL text scanning, no AWS API calls and no `terraform apply`.

## Likely touchpoints
- `src/iac_reviewer/` Python package
- `tests/` pytest tests
- `examples/terraform/` HCL fixtures
- `docs/ARCHITECTURE.md`, `docs/RULES.md`, `docs/ROADMAP_ALIGNMENT.md`
- `.github/workflows/iac-review.yml`
- `infra/terraform-intake.md`
