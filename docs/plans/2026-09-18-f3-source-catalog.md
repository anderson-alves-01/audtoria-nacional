# 0.3.9 — Registro Mestre de Fontes sintético

## Goal

Expor o catálogo de fontes com papel, classificação, finalidade e dry-run sintético. Fonte pública nunca vira crédito. Fonte restrita não ingere.

## Roadmap

F3.0 local. G0/G1/G3 oficial BLOCKED.

## Acceptance

- GET `/v1/data-sources` com `createsTaxCredit=false` e `officialIngestion=false`
- Dry-run IBGE aceito sem download
- Dry-run municipal RESTRICTED = 403
- tech_admin 403
- UI `/fontes`

## Evidence

`evidence/releases/0.3.9/`
