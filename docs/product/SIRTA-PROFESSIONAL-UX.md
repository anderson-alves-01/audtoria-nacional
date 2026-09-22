# SIRTA — Reformulação Profissional da Plataforma

**Documento:** Especificação de Produto, UX e Interface  
**Versão:** 1.0  
**Data-base:** 22 de setembro de 2026  
**Referência:** padrão executivo do Centro de Inteligência Preditiva do CFQ  
**Base técnica observada:** `feat/aws-prod-stack` @ `b7d843a`, implementação `0.3.101`

---

## 1. Decisão de reformulação

O SIRTA deixará de apresentar sua estrutura interna como uma coleção de páginas técnicas e passará a funcionar como uma plataforma executiva de inteligência e proteção da receita pública.

Posicionamento principal:

> **SIRTA — Plataforma Municipal de Inteligência e Proteção da Receita Pública**

Promessa de produto:

> **Auditar. Acompanhar. Recuperar.**

A reformulação preservará APIs, contratos, gates, regras de segurança, linhagem e separação entre dados oficiais, hipóteses e crédito validado. O trabalho será concentrado na arquitetura de informação, design system, shell, visualização, acessibilidade e experiência.

---

## 2. Diagnóstico do estado atual

### 2.1 Interface

Diagnóstico revisado em 22/09/2026 sobre `feat/aws-prod-stack` (`0.3.101`), antes da reformulação em `feat/professional-ui-v1`. Evidência em `evidence/releases/0.4.0/ui-baseline/`.

- o cabeçalho concentra 29 links em duas listas planas, sem grupos de módulo;
- a rota `/` abre saúde da plataforma, não a visão executiva;
- não existe sidebar, breadcrumb nem barra de contexto;
- `styles.scss` não contém o design system institucional (tokens, sidebar, componentes compartilhados);
- os 15 painéis já renderizam KPIs e gráficos via `ngx-echarts` quando há Gold, mas o gráfico está acoplado à página e a lineage (hash, endpoint, manifesto) permanece no corpo;
- `/setorial` ainda é lista de fontes com a flag `ingestAllowed`, sem visão executiva por setor;
- a versão `0.3.101` está fixada no cabeçalho (`app.shell.ts`) e no `package.json`.

### 2.2 Produto e operação

- a implementação registrada está em `0.3.101` no estado, no shell e no `package.json` da web;
- o branch principal público permanece muito atrás da linha em desenvolvimento;
- a URL publicada respondeu `502 Bad Gateway` durante a auditoria de 22/09/2026;
- o frontend atual é adequado como prova técnica e validação de contratos, mas não como produto para prefeito, secretário, auditor, procurador ou controlador.

### 2.3 Diretriz

Não fazer um “tema novo” sobre a navegação atual. A experiência deverá ser reconstruída sobre um shell modular e uma arquitetura de informação compatível com os cinco módulos do SIRTA.

---

## 3. Princípios herdados do projeto CFQ

1. Identidade visual executiva e institucional.
2. Logo e nome do produto com destaque, sem competir com os indicadores.
3. Hierarquia visual clara entre contexto, KPI, análise e evidência.
4. Paleta consistente, vinculada à identidade do produto.
5. Tipografia, títulos, tabelas, margens e espaçamentos padronizados.
6. Informação complexa organizada por níveis de leitura.
7. Painéis com narrativa: situação atual, evolução, comparação, causa e ação.
8. Dados oficiais acompanhados de fonte, competência e metodologia.
9. Experiência executiva distinta da experiência operacional.
10. Visual corporativo sóbrio, moderno e acessível.

---

## 4. Nova arquitetura de informação

### 4.1 Gestão Executiva da Receita

- Visão executiva;
- Dinheiro do Município;
- funil de recuperação;
- metas, evolução e alertas;
- resumo das transferências;
- maturidade e gates relevantes;
- painel público agregado.

### 4.2 Recuperação Tributária

- créditos identificados;
- validação e exigibilidade;
- achados e casos de auditoria;
- cobrança administrativa;
- pagamentos e parcelamentos;
- dívida ativa;
- Procuradoria;
- trilha do crédito.

### 4.3 Auditoria de Repasses

- transferências federais;
- ICMS/IPVA e repasses estaduais;
- previsto versus recebido;
- divergências e ocorrências;
- conciliação;
- evidências e fontes oficiais.

### 4.4 Inteligência Fiscal

- Cadastro 360;
- inteligência econômica;
- inteligência setorial;
- fontes e catálogo;
- qualidade e linhagem;
- regras de auditoria;
- mapa territorial.

### 4.5 Observatório da Reforma Tributária

- calendário IBS/CBS;
- impactos sobre receitas municipais;
- cenários não vinculantes;
- leiautes e documentos oficiais;
- prontidão municipal;
- pendências de homologação.

### 4.6 Governança e Operação

- diagnóstico;
- gates humanos;
- validação humana;
- uploads municipais;
- usuários, papéis e finalidade;
- saúde da plataforma;
- governança operacional;
- auditoria técnica.

---

## 5. Mapeamento das rotas atuais

| Rotas atuais | Destino na nova navegação |
|---|---|
| `/executivo`, `/financeiro`, `/funil`, `/publico` | Gestão Executiva da Receita |
| `/validacao`, `/achados`, `/casos-auditoria`, `/cobranca`, `/pagamentos`, `/divida-ativa`, `/procuradoria` | Recuperação Tributária |
| `/transferencias`, `/conciliacao-transferencias`, `/transferencias-estaduais` | Auditoria de Repasses |
| `/economia`, `/setorial`, `/cadastro-360`, `/fontes`, `/qualidade`, `/regras-auditoria` | Inteligência Fiscal |
| `/ibs-cbs`, `/calendario`, `/prontidao` | Observatório da Reforma Tributária |
| `/diagnostico`, `/gates`, `/validacao-humana`, `/upload-municipal`, `/operacao-governanca`, `/auditoria`, `/` | Governança e Operação |

As URLs existentes devem continuar funcionando por redirecionamento ou compatibilidade. A mudança de navegação não poderá quebrar bookmarks, testes ou links externos.

---

## 6. Shell profissional

### 6.1 Sidebar

- largura expandida de 264 px e recolhida de 80 px;
- marca SIRTA no topo;
- cinco módulos principais, Governança e favoritos;
- grupos recolhíveis;
- ícones consistentes;
- item ativo e subitem ativo claramente identificados;
- badges apenas para alertas relevantes;
- versão somente na tela “Sobre”, nunca no menu principal.

### 6.2 Topbar

- breadcrumb;
- município/tenant atual;
- seletor de território;
- seletor de competência;
- busca global/command palette;
- central de alertas;
- ajuda contextual;
- perfil do usuário;
- badge discreto de ambiente quando não for produção.

### 6.3 Barra de contexto dos dados

Toda página analítica deverá mostrar:

- município/território;
- competência;
- última atualização;
- nível de qualidade;
- homologação;
- fonte principal;
- botão “Ver evidências”.

### 6.4 Conteúdo

- grid responsivo de 12 colunas;
- largura fluida com limite visual adequado para leitura;
- header da página com título, descrição curta, estado e ações;
- filtros persistentes por módulo;
- skeleton durante carregamento;
- empty state com explicação e próxima ação;
- erros com correlação e opção segura de tentar novamente.

---

## 7. Design system

### 7.1 Cores

| Token | Cor | Uso |
|---|---|---|
| `primary-900` | `#0B1F3A` | sidebar, títulos e identidade |
| `primary-700` | `#163D63` | navegação ativa e ações principais |
| `teal-600` | `#0E7490` | inteligência e informação |
| `green-600` | `#16845B` | recuperado, conciliado, regular |
| `gold-500` | `#C7962D` | potencial, atenção e identidade pública |
| `orange-600` | `#C96820` | prazo e pendência |
| `red-600` | `#B63A48` | risco e bloqueio |
| `surface` | `#FFFFFF` | cartões e painéis |
| `background` | `#F4F7FB` | fundo da aplicação |
| `text` | `#172033` | texto principal |
| `muted` | `#667085` | texto secundário |
| `border` | `#DDE3EC` | divisores e contornos |

As cores não poderão ser o único meio de comunicar um estado.

### 7.2 Tipografia

- família principal: Inter ou Source Sans 3 autohospedada;
- títulos com pesos 600/700;
- corpo 400/500;
- números tabulares para valores financeiros;
- escala coerente de 12, 14, 16, 20, 24, 32 e 40 px.

### 7.3 Componentes obrigatórios

- AppShell;
- Sidebar e NavGroup;
- Topbar e Breadcrumb;
- PageHeader;
- ContextBar;
- KpiCard;
- TrendCard;
- ChartCard;
- DataTable;
- FilterBar;
- StatusChip;
- QualityBadge;
- SourceBadge;
- NonBindingBadge;
- EvidenceDrawer;
- AlertPanel;
- EmptyState;
- ErrorState;
- Skeleton;
- Modal/Drawer acessível;
- Toast;
- Pagination;
- Tabs;
- Stepper para fluxos de validação.

---

## 8. Novo Painel Executivo

### 8.1 Primeiro nível de leitura

- Receita sob gestão;
- potencial estimado, sempre identificado como estimativa;
- créditos identificados;
- créditos auditados;
- valor elegível;
- valor em cobrança;
- parcelamentos ativos;
- valor efetivamente recuperado;
- ISR;
- atualização e qualidade.

### 8.2 Visualizações

- evolução mensal/anual da arrecadação;
- funil Identificado → Auditável → Validado → Cobrança → Recuperado;
- waterfall de composição da receita;
- transferências previstas versus recebidas;
- divergências por materialidade;
- mapa territorial;
- matriz prioridade × recuperabilidade;
- alertas críticos e próximos prazos;
- resumo da dívida ativa;
- prontidão IBS/CBS.

Valores de potencial, crédito e recuperação nunca poderão ser somados ou apresentados como equivalentes.

---

## 9. Nova página de Inteligência Setorial

Título: **Inteligência Setorial**  
Subtítulo: presença econômica, indicadores oficiais e oportunidades de auditoria por setor.

### 9.1 Filtros

- UF;
- município;
- competência;
- setor;
- fonte;
- qualidade;
- homologação.

### 9.2 KPIs

- estabelecimentos cobertos;
- municípios com cobertura;
- indicadores publicados;
- fontes ativas;
- qualidade média;
- última atualização.

### 9.3 Setores

- Combustíveis — ANP;
- Energia — ANEEL/EPE;
- Telecomunicações — Anatel;
- Financeiro — Banco Central;
- Saúde — CNES/DATASUS.

### 9.4 Visualizações

- cards de setor;
- série histórica;
- distribuição territorial;
- ranking municipal;
- cobertura e qualidade por fonte;
- comparação entre setores;
- mapa quando houver granularidade compatível;
- painel de evidências e lineage em drawer.

### 9.5 Regra soberana

Exibir permanentemente, de forma discreta:

> Dados setoriais são referências de contexto e cruzamento. Não constituem crédito tributário nem autorizam cobrança.

Flags técnicas como `ingestAllowed`, hashes, endpoints e nomes internos não devem aparecer na leitura principal. Permanecerão disponíveis em “Ver evidências”.

---

## 10. Estados sem dados e não homologados

Uma página sem Gold autorizado não ficará parecendo quebrada. Ela deverá apresentar:

- ícone e título claros;
- motivo do estado vazio;
- fonte esperada;
- gate responsável;
- o que já está disponível;
- próxima ação permitida;
- link para evidências ou documentação;
- proibição explícita de inventar valores.

Não preencher gráficos com dados sintéticos em ambiente de demonstração oficial. Quando necessário, usar modo “Demonstração”, visualmente separado e identificado.

---

## 11. Visualização e evidência

Cada KPI ou gráfico terá:

- título orientado a negócio;
- período;
- unidade;
- fonte;
- competência;
- atualização;
- qualidade;
- homologação;
- metodologia;
- drawer de evidência com lineage, manifesto e checksum.

Metadados técnicos detalhados ficarão disponíveis sob demanda, sem poluir o painel executivo.

---

## 12. Arquitetura Angular proposta

```text
src/app/
├── core/
│   ├── auth/
│   ├── guards/
│   ├── interceptors/
│   ├── context/
│   └── observability/
├── layout/
│   ├── app-shell/
│   ├── sidebar/
│   ├── topbar/
│   └── context-bar/
├── shared/
│   ├── ui/
│   ├── charts/
│   ├── tables/
│   ├── states/
│   └── evidence/
├── features/
│   ├── executive/
│   ├── recovery/
│   ├── transfers/
│   ├── intelligence/
│   ├── tax-reform/
│   └── governance/
└── app.routes.ts
```

Diretrizes:

- lazy loading por módulo;
- configuração única de navegação;
- route metadata para breadcrumb, autorização e contexto;
- componentes standalone;
- serviços tipados;
- nenhum acesso HTTP direto em componentes de apresentação;
- adapter para gráficos;
- design tokens em CSS custom properties;
- tema claro como padrão e base preparada para tema escuro futuro.

---

## 13. Confiabilidade e versão

Antes da publicação da nova UI:

1. eliminar versão hardcoded no HTML;
2. usar build info gerado a partir do estado/versionamento da aplicação;
3. apresentar versão somente em “Sobre” e diagnóstico;
4. criar página de erro 404/500/503 profissional;
5. diagnosticar o `502` do ALB;
6. validar health check do frontend e target group;
7. preservar deep links e fallback do Angular no nginx;
8. incluir correlation ID no erro apresentado ao usuário;
9. validar cache dos assets com hash;
10. manter rollback da imagem anterior.

Nenhuma alteração de infraestrutura será aplicada sem autorização específica.

---

## 14. Acessibilidade e responsividade

- WCAG 2.2 AA;
- navegação completa por teclado;
- skip link;
- foco visível;
- landmarks e headings sem saltos;
- tabelas com cabeçalhos e descrições;
- gráficos com resumo textual e tabela alternativa;
- contraste mínimo aprovado;
- alvos de toque adequados;
- suporte a 390, 768, 1024, 1366, 1440 e 1920 px;
- sidebar adaptada para drawer em mobile;
- preferência de redução de movimento.

---

## 15. Plano de execução

### UX0 — Baseline e confiabilidade

- congelar screenshots e rotas atuais;
- registrar o `502` e a divergência de versões;
- criar branch exclusiva;
- garantir testes verdes antes da mudança;
- criar arquitetura de testes visuais.

### UX1 — Design system e shell

- tokens;
- tipografia;
- ícones;
- componentes base;
- sidebar, topbar, breadcrumb e context bar;
- empty/error/loading states.

### UX2 — Navegação e Painel Executivo

- agrupar rotas nos cinco módulos;
- preservar compatibilidade;
- implementar “Dinheiro do Município”;
- gráficos, KPIs, alertas e evidências.

### UX3 — Recuperação e Repasses

- fluxo do crédito;
- casos e validação;
- cobrança, pagamentos e dívida ativa;
- transferências e conciliação.

### UX4 — Inteligência Fiscal e Setorial

- Cadastro 360;
- economia;
- setorial;
- fontes, qualidade e regras;
- mapa e rankings.

### UX5 — Reforma Tributária e Governança

- observatório IBS/CBS;
- calendário;
- prontidão;
- gates, validação humana e operação.

### UX6 — Qualidade final

- responsividade;
- acessibilidade;
- performance;
- regressão visual;
- documentação;
- evidência;
- imagem candidata e rollback.

---

## 16. Critérios de aceite

1. Nenhuma tela possui navegação horizontal com dezenas de links.
2. Os cinco módulos são compreensíveis sem conhecer a arquitetura interna.
3. A home abre no Painel Executivo, não em `/health`.
4. Toda visualização informa fonte, competência, qualidade e homologação.
5. Metadados técnicos ficam disponíveis em evidências, sem dominar a tela.
6. Páginas vazias possuem orientação profissional e não fabricam dados.
7. Rotas antigas continuam válidas.
8. Nenhuma regra tributária ou gate humano muda de estado por causa do redesign.
9. Testes unitários, integração, acessibilidade e E2E ficam verdes.
10. Layout funciona nas resoluções definidas.
11. O frontend não possui versão hardcoded.
12. O deploy candidato possui health check e rollback documentados.
13. Lighthouse: acessibilidade ≥ 95 e boas práticas ≥ 90 nas páginas críticas.
14. A interface comunica separadamente potencial, indício, crédito validado e valor recuperado.
15. A nova experiência é adequada a apresentação para prefeito, secretário, auditor e órgão de controle.

---

## 17. Estratégia Git recomendada

- base: HEAD atual de `feat/official-public-ingest`;
- nova branch: `feat/professional-ui-v1`;
- PR empilhada inicialmente contra `feat/official-public-ingest`;
- não adicionar a reformulação ao PR técnico já muito extenso;
- commits atômicos por UX0–UX6;
- não fazer merge automático;
- preservar um tag ou SHA do baseline anterior;
- promover para `main` somente após decisão específica sobre a linha técnica existente.

---

## 18. Resultado esperado

O SIRTA deverá deixar de parecer uma interface de validação de APIs e passar a operar como um centro municipal de inteligência fiscal: sóbrio, confiável, executivo, auditável e orientado à decisão, mantendo a regra central:

> **Nenhuma cobrança sem validação.**
