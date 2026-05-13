# Team Brief: AWS Well-Architected IaC Reviewer

Build a portfolio-ready repository that implements the roadmap's second project: AWS Well-Architected IaC Reviewer.

Reference inputs:
- Parent roadmap: `../cloud-sa-devops-portfolio-roadmap.md` section `# 2. AWS Well-Architected IaC Reviewer`.
- Terraform planner reference: `../aws-incident-response-observability-lab/cloud_deploy_skill/skill/terraform-cloud-planner/references/aws-question-bank.md`.
- Context snapshot: `.omx/context/aws-well-architected-iac-reviewer-20260513T081500Z.md`.

Scope:
- Static Terraform scanner; no AWS credentials, no Terraform apply.
- Python CLI with tests.
- Terraform fixture examples for secure and insecure IaC.
- Markdown output report named `architecture-review.md`.
- GitHub Actions workflow for PR/repo automation.
- Docs explaining architecture and roadmap alignment.

Required Well-Architected pillars/check families:
- Security: public S3, permissive Security Groups.
- Reliability: RDS backups/Multi-AZ signals.
- Operational Excellence: CloudWatch logs/alarms and tags.
- Cost Optimization: oversized instances and Budget coverage.
- Performance Efficiency: Auto Scaling/cache hints.

Validation before completion:
- `python -m compileall src tests`
- `python -m pytest` if pytest available, otherwise a documented fallback test command.
- `terraform fmt -check -recursive examples infra` if Terraform available.
- Do not leave failing tests unaddressed.
