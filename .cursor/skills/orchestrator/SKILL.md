---
name: auditoria-orchestrator
description: Coordinate end-to-end implementation using the roadmap, gates and specialized skills.
---
# Orchestrator

Read `AGENTS.md`, `current-state.yaml`, `config/skills-policy.yaml`, roadmap and acceptance criteria. Build a dependency-aware task list and execute one bounded task at a time with the appropriate skill. This release uses sequential execution; do not activate parallel-agent or worktree workflows.

For every slice require: plan, implementation, tests, security review, evidence, state update and rollback. Re-run failing gates until resolved or genuinely blocked. Stop for credentials, real data, legal interpretation, destructive change, paid service, external publication or production deployment.

Never let a subtask mark the parent complete without integrated verification.
