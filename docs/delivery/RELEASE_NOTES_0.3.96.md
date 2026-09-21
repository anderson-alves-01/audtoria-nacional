# Release notes 0.3.96

## Summary

Activate BCB OLINDA `ExpectativasMercadoSelic` (Focus Selic by Copom meeting)
as PUBLIC_OPEN reference enrichment, distinct from annual Selic and from empty
trimestral Selic series.

## Technical

- Source: `BCB-OLINDA-EXPECTATIVAS-SELIC`
- Connector: `bcb_olinda_expectativas` with `horizon_field=Reuniao`
- Layout: `bcb-olinda-expectativas-selic-v1`
- Allowlist: Selic; baseCalculo=1; max_rows=8; silverCount=8
- Fixture: `tests/fixtures/official-snapshots/bcb-olinda-expectativas-selic-reuniao-top8.json`
- Migration: `0099_bcb_olinda_selic` → `0.3.96`

## Out of scope

- ExpectativasMercadoInflacao12Meses / 24Meses / Top5
- Remaining UF tabular activations (RJ IP-blocked, SP HTML-only, etc.)
