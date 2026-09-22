# Plan — F3 sectoral official sources (0.3.22)

## Goal

Catalog ANP, ANEEL, EPE, Anatel, BCB and CNES/DATASUS with verified official endpoints; expose an empty technical enrichment shell; keep ingest fail-closed until activation criteria are met.

## Roadmap

F3.2 items: `F3-SECTORAL-ANP`, `F3-SECTORAL-ANEEL-EPE`, `F3-SECTORAL-ANATEL`, `F3-SECTORAL-BCB`, `F3-SECTORAL-CNES`.

## Spec / ADR

- `AGENTS.md`, `docs/delivery/ROADMAP-SIRTA-2026.md` § fontes setoriais
- Source role: `REFERENCE_ENRICHMENT` only; never creates tax credit

## Components / files

- `contracts/sources/official-catalog.yaml`
- `apps/api/.../domain/sectoral_enrichment.py`
- `apps/api/.../application/sectoral_enrichment.py`
- `apps/api/.../entrypoints/sectoral_enrichment.py`
- `apps/api/.../application/official_ingest.py` (blocked connectors)
- `contracts/openapi/sirta-v1.yaml`
- `apps/web/.../sectoral-enrichment/`
- `alembic/versions/0025_sectoral_enrichment.py`
- tests unit/integration/Angular

## Data classification

PUBLIC_OPEN catalog entries; `fixture_kind: NONE`; status `DISCOVERED`. No live national ingest. CNES notes possible personal data → minimization required before any load.

## Security

`ensure_fiscal_read` on GET; POST always 409. Connectors in blocked set. No scraping.

## Migration / rollback

Additive schema_meta bump to 0.3.22; downgrade restores 0.3.21.

## Acceptance

- Six sources listed in catalog and data-sources API with `ingestAllowed=false`
- `/v1/sectoral-enrichment` empty shell; createsTaxCredit=false; POST 409
- Angular empty/loading/error states
- Targeted pytest + Angular tests pass

## Human gates

None advanced. Homologation of Gold remains pending.
