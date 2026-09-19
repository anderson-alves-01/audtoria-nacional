# Release notes 0.3.24

## Fatia

Conector RFB CNPJ com escopo territorial, retomada e política de EI; shell estadual ICMS/IPVA com proveniência RJ.

## Entregas

- Domínio `rfb_cnpj`: `territorial_scope` fail-closed, cursor de retomada, manifesto e exclusão de empresário individual do Gold.
- Parser streaming de Estabelecimentos com filtro por UF/município.
- Ingest RFB permanece 403 enquanto `territorial_scope=none` / sem `TECHNICALLY_APPROVED`.
- Catálogo estadual: RJ `PROVENANCE_VERIFIED` (CKAN CSV ICMS/IPVA); download bloqueado por filtro de IP da SEFAZ neste runtime.
- API/UI `/v1/state-transfers` e `/transferencias-estaduais` vazias; POST → 409; sem crédito.
- Migration aditiva `0027_rfb_state_transfers` (meta 0.3.24).

## Não feito

Ativação de ingest estadual (schema CSV não baixável aqui), carga RFB com território autorizado, setoriais ativados, piloto, produção, homologação humana.

## Rollback

Downgrade Alembic `0027` → `0026`; reverter catálogos/API/web se necessário.
