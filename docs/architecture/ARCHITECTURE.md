# Arquitetura de referência

## Componentes

- `web`: portal Angular responsivo.
- `admin`: administração isolada.
- `api`: FastAPI modular.
- `workers`: orquestração assíncrona e relatórios.
- `pipelines`: conectores e transformação Bronze/Silver/Gold.
- `rules-engine`: regras fiscais versionadas.
- `case-service`: casos, evidências e decisões.
- `audit-service`: eventos imutáveis.
- `ai-gateway`: RAG privado, políticas, DLP e ferramentas autorizadas.

## Armazenamento

- Cloud Storage: Bronze e documentos.
- BigQuery: Silver, Gold e analytics.
- PostgreSQL: transações, workflow e autorização.
- Redis: cache sem dados sensíveis persistentes.
- Vector store: índices autorizados e segregados por tenant.

## Princípios

- Monólito modular inicialmente; extração de serviços apenas por necessidade comprovada.
- Hexagonal por domínio.
- Eventos com transactional outbox.
- Contratos versionados e compatíveis.
- Observabilidade por `trace_id`, `tenant_id`, `run_id` e `case_id`, sem PII.
- Implantação independente de web, API e jobs.

## Ambientes

Local e dev usam dados sintéticos. QA usa sintéticos ou mascarados. Staging usa subconjunto mascarado controlado. Produção e DR são segregados, criptografados e auditados.

