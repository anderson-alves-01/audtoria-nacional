---
name: systematic-debugging
description: Use for bugs, failed tests, broken jobs, invalid SQL, integration failures or unexpected behavior before proposing a fix.
---
# Systematic Debugging - Auditoria Nacional

## Activation

Mandatory for any defect or failed gate in phases F0-F7. Read `config/skills-policy.yaml` before acting.

## Process

1. Capture the exact error, command, environment, version, `run_id` and affected component.
2. Reproduce with the smallest safe fixture. Never reproduce with production data unless explicitly authorized.
3. Inspect recent changes and trace data across component boundaries.
4. State one falsifiable root-cause hypothesis.
5. Test the hypothesis with one minimal, reversible change.
6. Add a failing regression test or executable reproduction.
7. Fix the root cause only; do not bundle unrelated refactoring.
8. Run targeted and impacted suites, then invoke `verification-before-completion`.

## Project-specific diagnostics

- Pipelines: compare manifest, checksum, schema, counts, Bronze/Silver/Gold and publication status.
- BigQuery: validate syntax, identifiers, referenced columns, region and migration order.
- API: correlate trace, request, authorization context, transaction and outbox.
- Frontend: verify contract version, network response, state and rendering.
- Security: do not print secrets or full fiscal/personal payloads while gathering evidence.

## Stop conditions

After three failed fix hypotheses, stop and request architectural review. Stop immediately if diagnosis requires credentials, real restricted data, production mutation or destructive action.

## Output

Record symptom, reproduction, evidence, root cause, fix, tests, residual risk and rollback under the current evidence directory.

