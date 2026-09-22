# Prompt Mestre — Reformulação Profissional do SIRTA no Cursor

Cole este conteúdo no modo Agent do Cursor, com o repositório aberto na linha mais recente de `feat/official-public-ingest`.

```text
@AGENTS.md
@current-state.yaml
@docs/delivery/ROADMAP-SIRTA-2026.md
@docs/delivery/HUMAN_DECISIONS_REQUIRED.md
@config/skills-policy.yaml
@apps/web/package.json
@apps/web/src/app/app.routes.ts
@apps/web/src/app/app.component.html
@apps/web/src/app/app.component.scss
@apps/web/src/styles.scss

MISSÃO

Reformular integralmente a experiência web do SIRTA para um padrão executivo, institucional e profissional inspirado no Centro de Inteligência Preditiva do CFQ.

Esta é uma transformação de arquitetura de informação, design system, navegação e dashboards. Não é uma simples troca de cores.

BASE E LIMITES

- Verifique a versão e o HEAD reais antes de agir. A referência observada em 22/09/2026 era implementation_version 0.3.97, mas use o estado atual do repositório.
- Não altere spec_version 0.3.0.
- Não mude gates humanos.
- Não invente dados.
- Não altere sem necessidade contratos da API.
- Não habilite cobrança, decisão administrativa ou regra tributária.
- Não faça Terraform apply, deploy ou alteração AWS.
- Não faça merge em main.
- Preserve todas as regras de tenant, território, finalidade, RBAC/ABAC, lineage e auditoria.
- A reformulação deverá usar somente dados já expostos pelas APIs existentes ou estados vazios profissionais.

GIT

1. Confirme que a árvore está limpa.
2. Atualize referências remotas sem reescrever histórico.
3. Parta do HEAD atual de feat/official-public-ingest.
4. Crie feat/professional-ui-v1.
5. Registre o SHA baseline.
6. Trabalhe em commits atômicos por fase UX0–UX6.
7. Push está autorizado somente para feat/professional-ui-v1.
8. Abra PR inicialmente contra feat/official-public-ingest.
9. Não faça merge automático.

FONTE DE VERDADE DE UX

Implemente a especificação “SIRTA — Reformulação Profissional da Plataforma v1.0”. Se o arquivo ainda não estiver no repositório, crie docs/product/SIRTA-PROFESSIONAL-UX.md com essa especificação antes de codificar.

DIAGNÓSTICO OBRIGATÓRIO

Antes de alterar:

1. execute npm ci, npm test e npm run build;
2. inventarie rotas, componentes, serviços e contratos consumidos;
3. capture screenshots das páginas críticas em desktop e mobile;
4. registre a navegação atual com mais de 30 links;
5. registre versão hardcoded no shell/package quando existir;
6. registre a ausência de design system global;
7. registre o estado atual de /setorial e dos dashboards;
8. crie evidence/releases/<nova-versao>/ui-baseline/;
9. não modifique backend durante esta etapa.

VERSÃO

- Trate a reformulação como a linha 0.4.0 do frontend, preservando a versão de especificação.
- Não declare 0.4.0 concluída antes de UX0–UX6 e todos os gates visuais estarem verdes.
- Remova versões hardcoded do HTML.
- Gere build info a partir de configuração/versionamento único.
- Exiba versão apenas em “Sobre”, diagnóstico e evidência.

ARQUITETURA DE INFORMAÇÃO

Organize a navegação em:

1. Gestão Executiva da Receita
   - Visão executiva
   - Dinheiro do Município
   - Funil de recuperação
   - Alertas e metas
   - Painel público

2. Recuperação Tributária
   - Créditos e validação
   - Achados
   - Casos de auditoria
   - Cobrança
   - Pagamentos/parcelamentos
   - Dívida ativa
   - Procuradoria

3. Auditoria de Repasses
   - Transferências federais
   - ICMS/IPVA estadual
   - Conciliação
   - Divergências e ocorrências

4. Inteligência Fiscal
   - Cadastro 360
   - Economia
   - Inteligência Setorial
   - Fontes
   - Qualidade e lineage
   - Regras de auditoria

5. Observatório da Reforma Tributária
   - IBS/CBS
   - Calendário
   - Impactos
   - Prontidão

6. Governança e Operação
   - Diagnóstico
   - Gates
   - Validação humana
   - Upload municipal
   - Operação e auditoria técnica
   - Saúde da plataforma

Preserve todas as URLs existentes por compatibilidade ou redirect explícito. A rota inicial deve abrir a visão executiva, nunca a página de health.

DESIGN SYSTEM

Crie tokens em CSS custom properties:

- primary-900 #0B1F3A
- primary-700 #163D63
- teal-600 #0E7490
- green-600 #16845B
- gold-500 #C7962D
- orange-600 #C96820
- red-600 #B63A48
- surface #FFFFFF
- background #F4F7FB
- text #172033
- muted #667085
- border #DDE3EC

Use Inter ou Source Sans 3 autohospedada, com fallback seguro. Use números tabulares para valores financeiros. Não dependa de fontes externas em runtime.

Crie componentes reutilizáveis:

- AppShell
- Sidebar/NavGroup
- Topbar
- Breadcrumb
- ContextBar
- PageHeader
- KpiCard
- TrendCard
- ChartCard
- FilterBar
- DataTable
- StatusChip
- QualityBadge
- SourceBadge
- NonBindingBadge
- EvidenceDrawer
- AlertPanel
- EmptyState
- ErrorState
- Skeleton
- Tabs
- Modal/Drawer
- Toast
- Pagination
- Stepper

Não copie CSS entre features. Não faça componentes monolíticos. Não renderize ícones por emojis. Use uma biblioteca de ícones consistente e acessível.

SHELL

- Sidebar expandida 264 px e recolhida 80 px.
- Grupos de navegação recolhíveis.
- Estado ativo claro.
- Topbar com breadcrumb, município, território, competência, busca, alertas e perfil.
- Barra de contexto com atualização, fonte, qualidade e homologação.
- Sidebar vira drawer em mobile.
- Conteúdo em grid responsivo de 12 colunas.
- Ambiente não produtivo recebe badge discreto.
- Versão não aparece no cabeçalho principal.

PAINEL EXECUTIVO

Implemente:

- Receita sob gestão;
- potencial estimado claramente identificado;
- créditos identificados;
- créditos auditados;
- valor elegível;
- em cobrança;
- parcelamentos ativos;
- recuperado;
- ISR;
- evolução temporal;
- funil financeiro;
- waterfall de receita;
- previsto versus recebido;
- divergências prioritárias;
- mapa territorial quando suportado;
- matriz prioridade × recuperabilidade;
- alertas e prazos;
- prontidão IBS/CBS.

Nunca somar potencial, indício, crédito validado e recuperação como se fossem equivalentes.

INTELIGÊNCIA SETORIAL

Recrie /setorial como página executiva:

- título “Inteligência Setorial”;
- filtros UF, município, competência, setor, fonte, qualidade e homologação;
- KPIs de cobertura, municípios, indicadores, fontes, qualidade e atualização;
- setores Combustíveis, Energia, Telecomunicações, Financeiro e Saúde;
- tabs ou cards por setor;
- série histórica;
- distribuição territorial;
- ranking municipal;
- cobertura/qualidade por fonte;
- comparação setorial;
- mapa apenas quando a granularidade for compatível;
- evidence drawer para endpoint, manifest, checksum e lineage.

Exiba aviso permanente e discreto:

“Dados setoriais são referências de contexto e cruzamento. Não constituem crédito tributário nem autorizam cobrança.”

Não exiba flags internas como ingestAllowed na camada executiva.

DASHBOARDS E GRÁFICOS

- Use uma biblioteca de gráficos compatível com Angular 18 por meio de um adapter interno.
- Não acople features diretamente à biblioteca.
- Todo gráfico deve ter título, unidade, período, legenda, tooltip, fonte, competência, qualidade e homologação.
- Forneça resumo textual e tabela alternativa acessível.
- Não use gráfico de pizza com muitas categorias.
- Não use eixo truncado quando distorcer comparação.
- Não fabrique série temporal.
- Estados sem Gold autorizado permanecem vazios e explicados.

EVIDÊNCIA E LINHAGEM

Retire hashes, endpoints, manifestos e nomes internos da leitura principal. Disponibilize-os no EvidenceDrawer, contendo:

- órgão mantenedor;
- dataset;
- URL oficial;
- competência;
- extração;
- qualidade;
- homologação;
- fórmula;
- metodologia;
- bronze SHA-256;
- landing manifest;
- lineage;
- quarentena.

EMPTY/ERROR/LOADING

- Crie skeletons consistentes.
- Empty state deve explicar motivo, fonte esperada, gate e próxima ação permitida.
- Erro deve ter mensagem humana, correlation ID e retry seguro.
- Crie páginas profissionais para 404, 500 e 503.
- Nunca preencher painel oficial com dado sintético silencioso.

CONFIABILIDADE

- Diagnostique localmente o caminho que pode produzir 502, sem acessar ou alterar AWS.
- Verifique nginx, porta, health check, SPA fallback e deep links.
- Produza runbook para ALB/target group, sem executar mudança cloud.
- Garanta cache de assets com hash e no-cache para index.html.
- Documente rollback para a imagem anterior.

ACESSIBILIDADE

- WCAG 2.2 AA.
- Navegação completa por teclado.
- Foco visível.
- Skip link funcional.
- Landmarks e headings corretos.
- Contraste verificado.
- Tabelas acessíveis.
- Gráficos com alternativa textual/tabular.
- prefers-reduced-motion.
- Testar 390, 768, 1024, 1366, 1440 e 1920 px.

ARQUITETURA ANGULAR

Reorganize progressivamente para:

src/app/core
src/app/layout
src/app/shared/ui
src/app/shared/charts
src/app/shared/tables
src/app/shared/states
src/app/shared/evidence
src/app/features/executive
src/app/features/recovery
src/app/features/transfers
src/app/features/intelligence
src/app/features/tax-reform
src/app/features/governance

- lazy loading por módulo;
- standalone components;
- route metadata para breadcrumb e autorização;
- configuração única de navegação;
- nenhum HTTP direto em componente de apresentação;
- models e adapters tipados;
- preserve os contratos existentes.

PLANO DE EXECUÇÃO

UX0 — baseline, inventário, screenshots, versão e testes.
UX1 — tokens, design system, componentes base e shell.
UX2 — navegação, visão executiva e Dinheiro do Município.
UX3 — Recuperação Tributária e Auditoria de Repasses.
UX4 — Inteligência Fiscal, Cadastro 360 e Setorial.
UX5 — Observatório IBS/CBS e Governança.
UX6 — acessibilidade, responsividade, performance, regressão visual e documentação.

LOOP AUTÔNOMO

Para cada UX:

1. escreva critérios de aceite;
2. escreva ou atualize testes;
3. implemente em pequenas fatias;
4. execute npm test e npm run build;
5. execute testes E2E/visuais das páginas alteradas;
6. revise responsividade e acessibilidade;
7. corrija falhas;
8. registre screenshots e resultados em evidence/releases/<versao>/ui/;
9. faça commit atômico;
10. continue automaticamente para a próxima fatia.

Não solicite confirmação para alterações locais, reversíveis e estritamente visuais. Pare apenas diante de:

- necessidade de alterar regra de negócio;
- quebra de contrato de API;
- dado real/restrito;
- decisão tributária ou jurídica;
- credencial;
- cloud apply/deploy;
- merge;
- ação destrutiva.

TESTES E GATES

- unitários Angular;
- integração de serviços e adapters;
- navegação de todas as rotas;
- compatibilidade de URLs antigas;
- acessibilidade automatizada;
- E2E das jornadas críticas;
- regressão visual desktop/mobile;
- build de produção;
- container web;
- secret scan;
- nenhuma regressão nos testes Python/API existentes.

Alvos Lighthouse para páginas críticas:

- acessibilidade >= 95;
- boas práticas >= 90;
- performance >= 85 no ambiente controlado.

CRITÉRIO DE CONCLUSÃO

Concluir somente quando:

- UX0–UX6 estiverem implementadas;
- os cinco módulos estiverem navegáveis;
- a home for executiva;
- /setorial estiver totalmente reformulada;
- metadados técnicos estiverem em evidence drawer;
- não houver versão hardcoded;
- rotas antigas funcionarem;
- testes e build estiverem verdes;
- screenshots desktop/mobile estiverem registradas;
- a interface não inventar dados;
- gates humanos permanecerem inalterados;
- PR estiver pronta para revisão, mas não mesclada.

RELATÓRIO FINAL

Entregue:

1. versão final;
2. branch e SHA baseline;
3. commits por UX;
4. páginas reformuladas;
5. componentes criados;
6. rotas e redirects;
7. dependências adicionadas e justificativa;
8. testes/resultados;
9. Lighthouse;
10. screenshots;
11. riscos e débitos;
12. diagnóstico do 502 e runbook sem aplicação cloud;
13. URL da PR;
14. confirmação de que não houve merge, deploy, cloud apply, dado inventado ou alteração de gate humano.

Comece pelo UX0. Não tente corrigir cada tela isoladamente antes de construir o design system e o novo shell.
```
