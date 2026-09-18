---
name: writing-plans
description: Use after an approved specification and before a multi-step implementation or roadmap phase.
---
# Writing Plans - Auditoria Nacional

## Activation

Mandatory at the start of F0-F7 and for any feature spanning more than one component.

## Plan location

`docs/plans/YYYY-MM-DD-<phase>-<feature>.md`

## Required header

- Goal and user outcome.
- Roadmap phase and epic.
- Approved specification and ADR references.
- Components and exact files.
- Consumed and produced interfaces.
- Data classification and allowed fixtures.
- Security and authorization impact.
- Migration and rollback strategy.
- Acceptance criteria and evidence path.
- Human gates.

## Task sizing

Use independently testable vertical slices, normally 15-45 minutes. Do not split setup, test and documentation away from the behavior that needs them. Each task must state exact files, commands, expected results and completion criteria.

## Constraints

No TBD/TODO placeholders. Do not assume cloud access, credentials or real data. Changes to tax interpretation, IAM, costs, production or destructive operations require an explicit checkpoint.

## Handoff

After self-review, the orchestrator may execute locally. Do not ask the user to choose an execution mode when the next action is safe and reversible.

