# Ciclo 2026-09-21 — BCB OLINDA Expectativas mensais IGP-M + Câmbio

## Fatia

Expandiu `BCB-OLINDA-EXPECTATIVAS-MENSAIS` com IGP-M e Câmbio
(baseCalculo=1) além de IPCA.

## Alterações

- Allowlist `[IPCA, IGP-M, Câmbio]`; layout mensais-v2; silverCount 24
- Medianas de prova: IPCA 0.4937; IGP-M 0.4327; Câmbio 5.17
- Fixtures oficiais mínimas + SNAPSHOT_URLS
- Migration `0093_bcb_olinda_igp_cambio` → `0.3.90`
- Próximo: IPCA Livres/Serviços/Administrados mensais ou trimestrais

## Rollback

Allowlist → `[IPCA]`; Alembic → `0092_bcb_olinda_mensais_ipca`.
