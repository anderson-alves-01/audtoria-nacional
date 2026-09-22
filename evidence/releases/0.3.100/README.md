# Fix 0.3.100 — UI 401 / sessão PUBLIC_OPEN

## Sintoma
Painéis mostravam “Não foi possível carregar o painel oficial.”  
API log: `GET /v1/dashboards/*` → **401** (web sem Bearer).

## Correção
- `GET /v1/auth/public-open-session` (flag `SIRTA_PUBLIC_OPEN_UI_BOOTSTRAP`)
- Interceptor Angular + `APP_INITIALIZER`
- JWKS/signing key no image; ECS env bootstrap

## Smoke ALB
- `/health` → `0.3.100`
- sessão → `PUBLIC_OPEN_UI_BOOTSTRAP`
- `/v1/dashboards/executivo` com token → **200** (published=false até ingest Gold no RDS PROD)
- `/v1/dashboards/cobranca` → **200** empty premium

## Residual
Gold oficial ainda não carregado no RDS PROD (só seed). UI deixa de falhar; painéis com Gold ficam empty até ingest autorizado.
