# Backlog inicial

> Documento legado de épicos da plataforma. O backlog executável vigente é `backlog/SIRTA-v0.3.yaml`. Em conflito, o YAML SIRTA e `SPRINT-PLAN-v0.3.md` têm precedência.

## EP-SIRTA-001 Fundação local (Sprint 0) — feito em 0.3.1

Workspace Python/Angular, Compose, health/ready, CI e seed sintético.

## EP-SIRTA-002 Identidade (Sprint 1) — feito em 0.3.1

OIDC, tenant, território, finalidade, isolamento e auditoria.

## EP-SIRTA-003+ (não autorizados em F0)

Validação tributária, cobrança, pipeline Gold e painéis permanecem bloqueados até nova autorização.

## Épicos legados da plataforma (não vigentes para F0)

## EP01 Fundação

- Criar workspace Python e Angular.
- Docker Compose com PostgreSQL, Redis, Keycloak e storage local.
- Health/readiness, logs JSON e tracing.
- CI com lint, testes, scans e build.
- Migrações e seed sintético.

## EP02 Identidade e segregação

- OIDC/MFA, tenants, territórios, perfis, finalidades e políticas.
- Testes negativos de acesso cruzado.
- Registro de login, consulta, alteração e exportação.

## EP03 Catálogo e ingestão

- CRUD de fontes e solicitações.
- Manifesto e execução de pipelines.
- Bronze/Silver/Gold, qualidade e quarentena.
- Dry-run, resume, idempotência e rollback.

## EP04 ISS

- Histórico e potencial.
- Painel por município, ano e atividade.
- Regras: ativo sem recolhimento, faturamento incompatível, retenção ausente, divergência setorial e devedor recorrente.
- Cenários conservador, provável e otimista.

## EP05 Casos

- Finding, triagem, caso, responsável, SLA, evidência, decisão e revisão.
- Exportação controlada de dossiê.

## EP06 Recuperação

- Apuração, lançamento, dívida, cobrança, parcelamento, judicialização e pagamento.
- Funil e ROI.

## EP07 DF

- Rankings ICMS/ISS 2024-2025.
- Setores definidos no escopo.
- Demais tributos e mapa por região administrativa.

## EP08 IA

- Ingestão documental aprovada.
- Pesquisa RAG com citação.
- Resumo e minuta.
- Avaliações de exatidão, autorização e vazamento.
