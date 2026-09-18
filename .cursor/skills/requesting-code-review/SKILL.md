---
name: requesting-code-review
description: Use after each independently testable slice and before a phase or release gate.
---
# Requesting Code Review - Auditoria Nacional

Provide the reviewer with goal, specification, roadmap phase, diff range, files, migrations, contracts, tests, evidence and known risks.

Request four lenses as applicable:

1. Specification compliance.
2. Code and architecture quality.
3. Security, LGPD, tenant isolation and chain of custody.
4. Data quality, methodology, reconciliation and explainability.

Severity:

- Critical/High: block progress.
- Medium: fix before phase gate unless explicitly accepted.
- Low: record with owner and target phase.

The implementer cannot approve its own critical security, fiscal methodology or release gate.

