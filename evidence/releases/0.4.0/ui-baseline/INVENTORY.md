# UX0 — baseline da UI

- Branch de origem: `feat/aws-prod-stack`
- SHA baseline: `b7d843aac98350e2b5664643f420ad93c219ab52`
- Branch de trabalho: `feat/professional-ui-v1`
- `implementation_version`: `0.3.101` (`current-state.yaml`, `apps/web/package.json`, `APP_IMPLEMENTATION_VERSION` em `apps/web/src/app/app.shell.ts`)
- `spec_version`: `0.3.0` (inalterada)
- Data: 2026-09-22

## Navegação atual

29 links em duas listas planas no cabeçalho (`APP_DASHBOARD_NAV` + `APP_UTILITY_NAV`). A rota `/` abre a página de saúde, não a visão executiva. A versão aparece no cabeçalho.

Painéis oficiais (15), todos em `DashboardPageComponent`: `/executivo`, `/financeiro`, `/economia`, `/operacao`, `/achados`, `/cobranca`, `/pagamentos`, `/divida-ativa`, `/transferencias`, `/ibs-cbs`, `/qualidade`, `/auditoria`, `/gates`, `/publico`, `/prontidao`.

Utilitários: `/` (saúde), `/fontes`, `/setorial`, `/transferencias-estaduais`, `/conciliacao-transferencias`, `/diagnostico`, `/regras-auditoria`, `/casos-auditoria`, `/notificacoes`, `/validacao`, `/validacao-humana`, `/cadastro-360`, `/upload-municipal`, `/funil`, `/operacao-governanca`, `/calendario`.

Componentes de página existentes e ainda sem rota: `collection`, `payments`, `active-debt`, `findings`, `procuradoria`, `pilot-readiness`. Os três primeiros têm equivalente nos painéis oficiais.

## Serviços HTTP no frontend

Chamadas diretas nos componentes de página (sem camada de apresentação separada) e em `PublicOpenSessionService` (`GET /v1/auth/public-open-session`). Dashboards: `GET /v1/dashboards/{id}`. Setorial: `GET /v1/sectoral-enrichment`.

## Design system

`styles.scss` tem cinco tokens locais e tipografia de sistema. Não há sidebar, breadcrumb nem componentes compartilhados de KPI, gráfico, empty ou evidência. Gráficos existem via `ngx-echarts` acoplado a `DashboardPageComponent`. `/setorial` lista fontes e a flag `ingestAllowed`.

## Screenshots

Captura local em `http://127.0.0.1:4200` (Chrome headless), antes da reformulação:

- `home-desktop.png`, `home-mobile.png`
- `executivo-desktop.png`, `executivo-mobile.png`
- `financeiro-desktop.png`
- `setorial-desktop.png`, `setorial-mobile.png`

## Fora de escopo nesta etapa

Nenhuma alteração de backend, contrato, gate, Terraform ou deploy.
