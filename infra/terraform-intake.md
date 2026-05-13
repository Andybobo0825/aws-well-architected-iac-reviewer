# Terraform Intake

Use this template before scanning or extending Terraform review coverage. Keep answers short and evidence-based. For portfolio demos, prefer low-cost defaults and avoid production-only services unless the project explicitly requires them.

## Detected Stack

- Application/runtime:
- Repository path scanned:
- Terraform root module(s):
- Provider(s):
- Current environment purpose: demo / staging / production / unknown
- Region assumption:

## Decisions

- Provider/region:
- Environment purpose:
- Runtime model:
- Scale expectations:
- Sizing assumptions:
- AWS services in scope:
- Availability target:
- Security/networking assumptions:
- Cost guardrail:
- Naming and required tags:

## Well-Architected Review Focus

| Pillar | Intake questions |
| --- | --- |
| Security | Are any buckets, security groups, or policies intentionally public? Is public ingress restricted to required ports and CIDRs? |
| Reliability | Does stateful data have backups? Is Multi-AZ required for this environment? |
| Operational Excellence | Are logs, alarms, ownership tags, and environment tags defined? |
| Cost Optimization | Are instance sizes demo-appropriate? Is an AWS Budget or cost guardrail present? |
| Performance Efficiency | Is scaling or caching required for the expected workload? |

## Terraform Plan Notes

- Files to scan:
- Resources/modules expected:
- Variables/outputs relevant to review:
- Known false-positive risks:

## Assumptions

- Static analysis cannot prove live AWS account state.
- Missing Terraform attributes may be inherited through modules or defaults.
- Demo environments may intentionally avoid production-grade redundancy to control cost.

## Open Questions

1.
2.
3.
