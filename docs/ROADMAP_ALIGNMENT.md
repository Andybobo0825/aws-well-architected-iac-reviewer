# Roadmap Alignment

This repository implements project 2 from the Cloud Solution Architect / DevOps portfolio roadmap: **AWS Well-Architected IaC Reviewer**.

## Roadmap goals

| Roadmap expectation | Repository implementation |
| --- | --- |
| Scan Terraform projects | Python CLI scans Terraform fixture or project paths |
| Check common architecture risks | Rule families cover Security, Reliability, Operational Excellence, Cost Optimization, and Performance Efficiency |
| Produce Markdown report | Reviewer writes `architecture-review.md` |
| Integrate with GitHub Actions | `.github/workflows/iac-review.yml` runs checks and uploads report artifacts |
| Support interview discussion | Docs explain architecture, constraints, rule families, and review tradeoffs |

## Portfolio message

The project shows how AWS architecture principles can be translated into automated engineering feedback. Instead of only writing Terraform examples, the reviewer demonstrates how a Cloud Solution Architect can build guardrails that help teams discuss risk earlier in the delivery lifecycle.

Suggested interview summary:

> I converted a focused subset of AWS Well-Architected review questions into a Terraform static reviewer. It runs locally or in GitHub Actions, flags common security, reliability, operational, cost, and performance risks, and produces a Markdown architecture review that can be discussed during pull requests.

## Scope decisions

- **Terraform first**: the roadmap allows Terraform or CloudFormation; this repository starts with Terraform to keep implementation and fixtures focused.
- **Static review**: no AWS credentials or live account access are needed, which makes the project safe for public portfolio review.
- **Markdown report**: `architecture-review.md` is human-readable and easy to attach to pull requests.
- **Transparent rules**: rule IDs and recommendations should remain understandable to both engineers and architects.

## Future extensions

- CloudFormation parser support.
- SARIF output for GitHub code scanning annotations.
- Pull-request comment publishing for summarized findings.
- Severity configuration per environment such as demo, staging, or production.
- Additional Well-Architected checks for IAM least privilege, encryption, backup retention, and observability maturity.
