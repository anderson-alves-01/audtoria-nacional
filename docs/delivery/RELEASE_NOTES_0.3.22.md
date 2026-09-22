# Release notes 0.3.22

## Fatia

Catálogo e shell técnico de fontes setoriais oficiais (ANP, ANEEL, EPE, Anatel, BCB, CNES/DATASUS).

## Entregas

- Seis entradas `DISCOVERED` / `fixture_kind: NONE` em `contracts/sources/official-catalog.yaml` com endpoints oficiais verificados.
- Conectores bloqueados em `official_ingest` (`anp_revendedores_api`, `aneel_ckan_open`, `epe_open_files`, `anatel_dados_gov`, `bcb_sgs_olinda`, `cnes_datasus_open`).
- `GET/POST /v1/sectoral-enrichment` — shell vazio; `createsTaxCredit=false`; `ingestEnabled=false`; POST → 409.
- Tela `/setorial` com loading/empty/erro.
- Migration aditiva `0025_sectoral_enrichment` (meta 0.3.22).

## Não feito

Backfill FPM/RREO/DCA, ICMS/IPVA estadual, RFB territorial, ativação de carga setorial, piloto, produção, homologação humana.

## Rollback

Downgrade Alembic `0025` → `0024`; remover rota/router se necessário.
