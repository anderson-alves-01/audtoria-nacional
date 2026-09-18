---
name: verification-before-completion
description: Use before claiming any task, phase, bugfix, pipeline, release or deployment is complete.
---
# Verification Before Completion - Auditoria Nacional

No completion claim is allowed without fresh evidence from the current revision.

## Required verification

1. Map every acceptance criterion to a command, test, query or inspected artifact.
2. Run the phase-specific gates defined in `config/skills-policy.yaml`.
3. Confirm the command exit status and inspect relevant output; do not infer success from silence.
4. Verify no restricted data, secrets or raw payloads leaked into logs or artifacts.
5. Verify contracts, migrations, lineage, authorization and rollback when applicable.
6. Save concise evidence and update `current-state.yaml`.

## Verdicts

- `GO`: every mandatory criterion has current evidence.
- `GO_WITH_RISK`: only explicitly accepted non-blocking risks remain.
- `NO_GO`: a mandatory gate failed, was skipped or cannot be proven.

Never convert missing evidence into `GO_WITH_RISK`. Production deployment always remains a human gate.

