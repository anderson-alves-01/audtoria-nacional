# Release notes 0.3.23

## Fatia

Controles fail-closed de backfill para FPM mensal e demonstrativos SICONFI (RREO/DCA/RGF).

## Entregas

- Domínio `backfill_controls`: hard_cap de `max_entes_per_run`, gate de disco, partição `exercício:período`, métricas de volume/tempo/armazenamento, sem wrap silencioso após `COMPLETE`.
- Settings `official_max_entes_hard_cap` (25) e `datalake_min_free_bytes` (64 MiB).
- Catálogo: `max_entes_per_run: 5` em RREO/DCA/RGF; FPM com `resource_url_by_competence`.
- Integração DCA no fluxo oficial de ingestão com fixtures.
- Migration aditiva `0026_controlled_backfill` (meta 0.3.23).

## Não feito

Carga nacional ilimitada, ICMS/IPVA estadual ativado, RFB territorial com download, ativação setorial, piloto, produção, homologação humana.

## Rollback

Downgrade Alembic `0026` → `0025`; reverter settings/catálogo se necessário.
