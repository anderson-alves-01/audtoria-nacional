---
name: quality-release-gate
description: Validate behavior, contracts, migrations, security and release evidence.
---
# QA and Release

Derive tests from acceptance criteria and risks. Run format, lint, unit, integration, contract, migration, SQL, E2E, accessibility, performance and security tests as applicable. Verify rollback and data reconciliation.

Create an evidence folder containing commands, machine-readable results and `verdict.md`. Do not publish. Return GO only when every mandatory gate is green.

