# Rule Catalog

This repository uses a deterministic static Terraform scanner to produce an `architecture-review.md` report. The rules are intentionally lightweight for portfolio and pull-request feedback: they inspect Terraform text only and never call AWS APIs, download providers, or run `terraform apply`.

## Demo defaults

- Region examples default to `ap-northeast-1`, matching the portfolio/demo guidance from `TEAM_BRIEF.md`.
- Fixtures are scanner inputs, not deployable reference architectures. Do not apply them without replacing placeholder AMIs, subnet IDs, passwords, and bucket names.
- Secure examples prefer low-cost signals: private network ranges, tags, CloudWatch logs/alarms, budgets, small instance classes, Auto Scaling hints, and cache hints.
- Insecure examples deliberately include findings so regression tests and demo reports can show each Well-Architected pillar.

## Implemented checks

| Rule ID | Pillar | Severity | What it flags | Secure fixture signal |
| --- | --- | --- | --- | --- |
| `SEC-S3-PUBLIC` | Security | High | Public S3 ACLs, disabled public-access-block controls, or bucket policies that grant S3 access to `Principal = "*"`. | Private bucket with all public access block controls set to `true`. |
| `SEC-SG-PUBLIC-INGRESS` | Security | High | Security group ingress open to `0.0.0.0/0` or `::/0` on all ports or sensitive ports such as SSH, RDP, database, Redis, or Elasticsearch. | Private CIDR ingress only for the demo application port. |
| `REL-RDS-BACKUP` | Reliability | Medium | RDS instances or clusters without `backup_retention_period` of at least one day. | `backup_retention_period = 7`. |
| `REL-RDS-MULTIAZ` | Reliability | Medium | RDS instances without an explicit `multi_az = true` resilience signal. | `multi_az = true` for the database fixture. |
| `OPS-CW-LOGS` | Operational Excellence | Medium | No `aws_cloudwatch_log_group` resource in the scanned Terraform set. | Application log group with retention. |
| `OPS-CW-ALARMS` | Operational Excellence | Medium | No `aws_cloudwatch_metric_alarm` resource in the scanned Terraform set. | Error alarm fixture. |
| `OPS-TAGS` | Operational Excellence | Low | AWS resources without a `tags` block for ownership, environment, or cost allocation. | Shared demo tags on taggable resources. |
| `COST-EC2-OVERSIZED` | Cost Optimization | Medium | EC2 instances using oversized classes such as `*.24xlarge` or metal sizes for a demo workload. | Small launch template instance type. |
| `COST-BUDGET` | Cost Optimization | Medium | No `aws_budgets_budget` resource in the scanned Terraform set. | Monthly budget capped at a demo-friendly amount. |
| `PERF-SCALING` | Performance Efficiency | Low | Compute resources without Auto Scaling or app autoscaling resources. | Auto Scaling group around the launch template. |
| `PERF-CACHE` | Performance Efficiency | Low | Compute resources without an obvious cache or managed read-optimization resource. | ElastiCache Redis cluster fixture. |

## Fixture map

- `examples/terraform/insecure/main.tf` intentionally triggers the rule families with a public S3 bucket, public SSH ingress, RDS without backups or Multi-AZ, missing observability, missing tags, no budget, oversized EC2, and no scaling/cache signals.
- `examples/terraform/secure/main.tf` demonstrates the positive signals that should keep this scanner quiet for the implemented rules while staying static and low-cost for demo review.

## Limitations

The scanner is not a full Terraform or HCL evaluator. It does not resolve modules, variables, dynamic blocks, IAM policy documents, provider defaults, or environment-specific exceptions. Treat findings as pull-request review prompts and document accepted risk with owner, context, and expiry date.
