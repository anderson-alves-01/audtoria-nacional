# UX1–UX6 — interface profissional

- Branch: `feat/professional-ui-v1`
- Baseline: `b7d843aac98350e2b5664643f420ad93c219ab52` (`feat/aws-prod-stack`)
- Interface: `0.4.0` (`apps/web/package.json` e `APP_IMPLEMENTATION_VERSION`)
- API / `implementation_version`: permanece `0.3.101`
- `spec_version`: `0.3.0`

## O que mudou

- Shell com sidebar de 6 grupos, trilha, contexto, busca na navegação e drawer no mobile.
- `/` abre `/executivo`. Saúde ficou em `/saude`. Versão só em `/sobre`.
- Tokens institucionais e Source Sans 3 latina autohospedada (`@fontsource/source-sans-3`).
- KPI, gráfico (adapter `app-chart-card` sobre ngx-echarts), empty, error, skeleton e evidence drawer.
- `/setorial` como Inteligência Setorial, sem a flag `ingestAllowed` na lista. Série só se a API publicar itens.
- Páginas `/erro` (500), `/indisponivel` (503) e rota desconhecida (404).
- `nginx` envia `no-cache` no HTML. Runbook em `docs/ops/WEB-502-RUNBOOK.md`, sem apply.

## Testes

- UX0: `npm test` — 44 SUCCESS (Chrome headless), antes da reformulação.
- Depois: `npm test` — 46 SUCCESS.
- `npm run build` — sucesso. Chunk inicial ~416 kB. ECharts fica em chunk separado.

## Screenshots

`evidence/releases/0.4.0/ui/`. Sem API local, os painéis mostram falha de carga, não dado inventado.

## Fora desta entrega

Sem merge, deploy, Terraform apply, alteração de gate humano ou de contrato da API.
