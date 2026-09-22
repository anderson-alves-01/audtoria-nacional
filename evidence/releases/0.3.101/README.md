# 0.3.101 — frontend shell compacto + 15 painéis unificados

## Causa do “painel não aparece”
1. Nav antiga ocupava quase o viewport (conteúdo só ao rolar).
2. Rotas inconsistentes (cobrança/achados/etc. fora do DashboardPage).
3. Troca entre painéis reutilizava o componente sem recarregar (`route.data`).

## Correção
- Shell sticky compacto; 15 painéis oficiais na mesma nav.
- Todos os 15 paths → `DashboardPageComponent`.
- Recarga ao trocar rota + sessão PUBLIC_OPEN antes do GET.
- Empty state explícito (“Painel aberto — sem Gold”).

## PROD
- Tag `0.3.101` web (+ api versão alinhada)
- ALB: painel executivo carrega; sem Gold no RDS → empty premium (esperado)
