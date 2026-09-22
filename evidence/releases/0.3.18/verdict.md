# 0.3.18 — F5 findings, cases, human-validation, notifications, collection

## Verdict

PASS for targeted unit/integration/Angular coverage of F5-FINDINGS-CASES,
F5-HUMAN-VALIDATION, F5-NOTIFICATIONS and F5-COLLECTION. Empty technical shells
only; no tax credit, no legal commands, no real notification send, no public
credit publication. G0/G4/G5 remain BLOCKED.

## CI root cause fixed this cycle

HEAD imported `sirta_api.entrypoints.notifications` and
`sirta_api.entrypoints.collection_panel` without shipping the modules, which
broke the Python job (`ModuleNotFoundError`). Modules, tests and web shells are
included in this push.

## Notes

Ver `docs/delivery/RELEASE_NOTES_0.3.18.md`.
Migration `0021_findings_human_validation` updates schema_meta only.
Roadmap stage remains `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`.
