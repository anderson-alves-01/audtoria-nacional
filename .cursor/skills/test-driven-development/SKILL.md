---
name: test-driven-development
description: Use before implementing domain behavior, APIs, authorization, calculations, bugfixes and pipeline transformations.
---
# Test-Driven Development - Auditoria Nacional

## Profiles

Read the `tdd_profiles` section of `config/skills-policy.yaml`.

### Strict RED-GREEN-REFACTOR

Required for domain rules, tax calculations, authorization, tenant isolation, case workflow, API behavior, idempotency and bugfixes.

1. Write one behavioral test.
2. Run it and observe the expected failure.
3. Implement the minimum behavior.
4. Run targeted and impacted tests.
5. Refactor only while green.

### Contract-first data testing

For pipelines and SQL, first create synthetic input, expected manifest, quality outcome, row counts and Gold result. Prove invalid records quarantine, reexecution does not duplicate and rollback removes only publication visibility.

### Validation-first infrastructure

For Terraform/configuration, write or update validation, policy and plan assertions before changing configuration. No apply is authorized by this skill.

### UI behavior-first

Define component or E2E behavior before implementation. Visual exploration may precede tests only when explicitly labeled disposable; production UI requires automated regression coverage.

Generated code is verified through generation and contract tests instead of hand-edited tests.

