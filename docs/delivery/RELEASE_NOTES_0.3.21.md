# Release notes 0.3.21

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

## Nesta fatia

- Correção CI: `ruff format`/`E501` em `pilot_readiness`, `dashboards` e testes.
- `GET/POST /v1/municipal-uploads` — slots restritos com quarentena/tenant; `uploadEnabled=false`; POST 409; sem amostra.
- `GET/POST /v1/cadastro-360` — sujeitos vazios; `piiPresent=false`; `territoryInvented=false`; minimização; POST 409.
- Telas `/upload-municipal` e `/cadastro-360`.
- Migration aditiva `0024_municipal_cadastro_shells` (meta 0.3.21).

## Não concluído

Backfill nacional FPM/RREO/DCA, fontes estaduais ICMS/IPVA, RFB territorial, setoriais, piloto institucional, produção e homologação humana.
