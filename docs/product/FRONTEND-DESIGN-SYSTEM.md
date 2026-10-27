# Sistema de design Meridiano — frontend BI do SIRTA / Tax Better

**Versão:** 1.0 · **Data:** 27/10/2026 · **Escopo:** somente frontend (`apps/web`). Contratos e endpoints da API não mudam. A autorização continua na API.

## 1. Princípios

1. Dado ausente aparece como `—` e fica fora de somas e escalas. Nada vira zero.
2. Nenhum número é inventado. Todo painel diz a fonte e o que ficou de fora.
3. "Não é crédito tributário" e "Cria crédito: não" continuam visíveis.
4. Todo gráfico tem tabela alternativa (botão "Ver tabela").
5. Tema escuro é o padrão; o claro é escolha do usuário (`localStorage` `sirta.theme`) e respeita `prefers-color-scheme` na primeira visita.

## 2. Tokens (`apps/web/src/styles.scss`)

| Grupo | Tokens |
| --- | --- |
| Fundo e superfície | `--bg`, `--bg-elev`, `--surface`, `--surface-2`, `--surface-3`, `--line`, `--line-strong` |
| Texto | `--text`, `--text-2`, `--muted`, `--on-accent` |
| Marca e estado | `--accent`, `--accent-strong`, `--accent-soft`, `--info`, `--warn`, `--danger`, `--ok` (+ `-soft`) |
| Dados | `--d1`…`--d8` (categórica), `--seq-1`…`--seq-5` (sequencial), `--null-fill` (sem valor) |
| Forma e tipografia | `--r`, `--r-sm`, `--r-lg`, `--sp-1`…`--sp-6`, `--shadow-1`, `--shadow-2`, `--font-ui` (Inter), `--font-num` (JetBrains Mono) |

Nomes antigos (`--paper`, `--ink`, `--green`, `--gold`, `--primary-*`, `--sirta-*`) são apelidos dos tokens novos e podem ser removidos num ciclo futuro de depreciação. Não há cores fixas em `*.scss`. As únicas exceções são as rampas sequenciais e as cores de região do mapa hexagonal (`geography-adapter.ts`, `hex-layout.ts`), que precisam de luminância numérica e têm testes próprios.

Contraste conferido (texto contra fundo efetivo, 4,5:1 para texto normal e 3:1 para texto grande) nos dois temas em Visão geral, Integração, Administração, Visão executiva, Dinheiro do Município, Validação, Sobre e Entrar: nenhuma falha em 296 + 62 + 67 + 56 + 28 + 34 + 28 + 5 trechos de texto por tema.

## 3. Componentes compartilhados

| Componente | Pasta | Uso |
| --- | --- | --- |
| `app-panel` | `shared/ui` | Cartão com título, subtítulo, fonte e ações |
| `app-kpi-card` | `shared/ui` | Indicador com rótulo, valor, meta, tipo e mini-série (só com ≥ 2 números reais) |
| `app-badge` | `shared/ui` | Etiqueta de estado (`neutral`, `accent`, `ok`, `warn`, `danger`, `info`) |
| `app-tabs` | `shared/ui` | Abas com setas, Home e End |
| `app-filter-bar` | `shared/ui` | Filtros ativos como chips removíveis |
| `app-bi-chart` | `shared/bi` | ECharts temado: barras, linha, área, treemap, funil, mapa de calor, dispersão |
| `app-data-table` | `shared/bi` | Tabela virtual: ordenar, filtrar por coluna, agrupar, redimensionar, ocultar colunas, gaveta de detalhe, CSV do que está na tela |
| `app-empty-state`, `app-error-state`, `app-skeleton` | `shared/states` | Estados vazio, erro e carregamento |

## 4. Interação de BI

- **Filtro cruzado:** clique seleciona, Shift soma, categorias não escolhidas ficam esmaecidas. Cada gráfico ignora o próprio filtro para continuar mostrando as demais categorias.
- **Detalhamento:** duplo clique desce um nível (imposto → fato gerador → órgão); "Subir um nível" volta.
- **Faixa:** arrastar no eixo seleciona várias categorias.
- **Estado na URL:** `f.<dimensão>=a~b` e `drill=a~b`; a visão é compartilhável. Visões salvas ficam no navegador (`sirta.views.<tela>`) e guardam só filtros.
- **Comparação de períodos:** diferença e variação só existem quando os dois lados têm valor gravado.
- **Paleta de comandos:** `Ctrl/Cmd + K` abre módulos e ações; `Esc` fecha. Painéis abertos viram abas (máximo de seis soltas, fixadas ficam).

## 5. Desempenho

Rotas dos módulos carregam sob demanda (`loadComponent`). Pacote inicial: 653,11 kB → 402,60 kB brutos (157,21 kB → 112,66 kB transferidos). O ECharts continua em chunk próprio, carregado só nas telas com gráfico.

## 6. Acessibilidade

Link para pular ao conteúdo, marcos `main` e `nav`, `aria-label` em todos os controles verificados, foco visível, `prefers-reduced-motion` respeitado, navegação por teclado na paleta, nas abas e na tabela. Idioma `pt-BR`.

## 7. Verificação e reversão

- `npx ng test --watch=false --browsers=ChromeHeadless` (98 testes) e `npx ng build`.
- Evidências por fase em `evidence/ops/frontend-bi-f3-20261027.txt`, `frontend-bi-f4-20261027.txt` e `frontend-bi-f5-20261027.txt`.
- Reversão: `git revert` do commit da fase; as imagens publicadas anteriores continuam disponíveis no ECR.
