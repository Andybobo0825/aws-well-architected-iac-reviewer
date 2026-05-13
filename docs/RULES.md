# Rule Catalog

The reviewer performs static Terraform checks that map portfolio-friendly IaC signals to AWS Well-Architected pillars. It never calls AWS APIs and never runs `terraform apply`.

| Rule ID | Pillar | Severity | What it detects | Example remediation |
| --- | --- | --- | --- | --- |
| `SEC-S3-PUBLIC` | Security | High | Public S3 ACLs, disabled public access block, or anonymous bucket policies. | Keep buckets private; use CloudFront OAC, signed URLs, or explicit documented exceptions. |
| `SEC-SG-PUBLIC-INGRESS` | Security | High | Security group ingress from `0.0.0.0/0` or `::/0` on all/sensitive ports. | Restrict CIDR ranges, use private connectivity, and document public endpoints. |
| `REL-RDS-BACKUP` | Reliability | Medium | RDS resources without automated backup retention. | Set `backup_retention_period` to at least one day for demos and align production to RPO/RTO. |
| `REL-RDS-MULTIAZ` | Reliability | Medium | RDS instances without explicit Multi-AZ configuration. | Enable `multi_az` for production-like workloads or document a low-cost demo exception. |
| `OPS-CW-LOGS` | Operational Excellence | Medium | No CloudWatch log group in the Terraform project. | Add workload log groups with retention. |
| `OPS-CW-ALARMS` | Operational Excellence | Medium | No CloudWatch metric alarm in the Terraform project. | Add alarms for health, latency, errors, saturation, or cost signals. |
| `OPS-TAGS` | Operational Excellence | Low | AWS resources without tags. | Add `Project`, `Environment`, `Owner`, and `ManagedBy` tags. |
| `COST-EC2-OVERSIZED` | Cost Optimization | Medium | EC2 instance types that are oversized for demo/portfolio use. | Use small burstable/Graviton instances unless load testing justifies capacity. |
| `COST-BUDGET` | Cost Optimization | Medium | Missing AWS Budget resource. | Add a monthly budget and notification policy. |
| `PERF-SCALING` | Performance Efficiency | Low | Compute resources without Auto Scaling signals. | Add ASG/App Auto Scaling or document fixed-capacity constraints. |
| `PERF-CACHE` | Performance Efficiency | Low | Compute resources without cache/read optimization signals. | Consider ElastiCache, DynamoDB, CDN, or application-level caching notes. |

## Fixture Coverage

- `examples/terraform/insecure-sample/` intentionally triggers Security, Reliability, Operational Excellence, Cost Optimization, and Performance Efficiency findings.
- `examples/terraform/secure-sample/` demonstrates a low-cost portfolio/demo baseline: private S3, constrained ingress, backup/Multi-AZ signals, CloudWatch logs/alarms, Budget, Auto Scaling, cache, and tags.

## Terraform Planner Alignment

The sample fixtures follow the Terraform planner reference defaults for portfolio/demo work: no credentials, no apply, no NAT Gateway/WAF/Route 53/TLS by default, CloudWatch retention kept short, and budget coverage included for cost guardrails.
