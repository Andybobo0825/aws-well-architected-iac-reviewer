# Architecture

## System purpose

The AWS Well-Architected IaC Reviewer is a local static-analysis CLI for Terraform repositories. It reads Terraform files from a target directory, evaluates a curated set of rule families, and writes a Markdown architecture review report.

The design favors transparent review logic over deep Terraform execution. It should be easy for a reviewer to understand why a finding was raised and which AWS Well-Architected pillar it maps to.

## Non-goals

- No AWS API calls.
- No AWS credentials.
- No Terraform state access.
- No `terraform init`, `terraform plan`, or `terraform apply` dependency.
- No claim that findings are a complete Well-Architected Review.

## Components

```text
Terraform project path
        │
        ▼
File discovery
        │
        ▼
Terraform text/HCL intake
        │
        ▼
Rule engine
        │
        ├── Security checks
        ├── Reliability checks
        ├── Operational Excellence checks
        ├── Cost Optimization checks
        └── Performance Efficiency checks
        │
        ▼
Finding model
        │
        ▼
Markdown report renderer
        │
        ▼
architecture-review.md
```

## Data flow

1. **Input selection**: the CLI receives a Terraform directory or file path.
2. **Discovery**: the reviewer locates Terraform files such as `*.tf` under the selected path.
3. **Intake**: file content and lightweight resource signals are normalized for rule evaluation.
4. **Rule evaluation**: each rule emits zero or more findings with severity, pillar, evidence, and remediation text.
5. **Report rendering**: findings are grouped by pillar and written to `architecture-review.md`.

## Rule model

A finding should contain enough context for architecture discussion:

| Field | Purpose |
| --- | --- |
| Rule ID | Stable identifier for tests and documentation |
| Pillar | Well-Architected pillar mapping |
| Severity | Review priority such as low, medium, high, or critical |
| Resource/file evidence | Where the signal was found |
| Rationale | Why the signal matters |
| Recommendation | Practical remediation guidance |

## Safety model

The reviewer treats Terraform as source text and does not evaluate live cloud state. This keeps local runs safe for portfolio usage and interview demonstrations.


## Extensibility

Add new checks by extending the rule catalog and pairing each rule with fixture coverage:

1. Add or update a rule implementation.
2. Add secure and insecure Terraform examples.
3. Add unit tests that prove the expected finding behavior.
4. Document the rule in `docs/RULES.md`.
5. Confirm `architecture-review.md` output remains readable.

## Operational considerations

- Keep rules deterministic so pull-request output is stable.
- Prefer clear findings over clever heuristics.
- Keep severities conservative when static text cannot prove intent.
- Surface assumptions in the report rather than hiding uncertainty.
