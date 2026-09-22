# Runbook — 502 da interface web (sem apply)

Diagnóstico local. Não altera AWS, target group, imagem nem DNS.

## O que o 502 costuma indicar

O ALB recebeu a conexão e o target do serviço web (ou da API, se o path foi para o grupo errado) não respondeu saudável. A interface em si não gera 502; o nginx do container ou o target group sim.

## Checagens locais, sem cloud

1. `apps/web/nginx.prod.conf` escuta na porta 80 e faz `try_files` para `index.html`. Deep links (`/executivo`, `/setorial`) caem no SPA. Não há `proxy_pass` nesse arquivo: `/v1` e `/health` precisam ir ao target group da API no balanceador, não ao container web.
2. `apps/web/nginx.conf` (compose local) encaminha `/health`, `/ready` e `/v1/` para `api:8080`. Se a API não sobe, esses paths falham no proxy. A página HTML continua servida pelo fallback.
3. O health check do target web deve pedir `/` ou um arquivo estático na porta 80 do nginx, não `/v1`. Pedir `/health` no target web de produção cai no `index.html` (SPA) e pode ser marcado saudável por engano, ou falhar se o health check exigir JSON.
4. `index.html` sai com `Cache-Control: no-cache`. Assets com hash no nome podem ser imutáveis. Um `index.html` antigo em cache aponta para bundles que não existem mais e o browser mostra falha de carga, não necessariamente 502.
5. Rollback da interface: publicar de novo a imagem web anterior já existente no registro. Não construir nem aplicar Terraform neste runbook.

## O que não fazer daqui

Não alterar listener, target group, security group ou task definition sem autorização explícita de deploy.
