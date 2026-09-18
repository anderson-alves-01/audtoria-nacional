# Auditoria Nacional - SIRTA Municipal

Plataforma segura de inteligência fiscal, auditoria e recuperação de receitas para municípios, estados, Distrito Federal e órgãos de controle.

Este repositório é o ponto de partida para desenvolvimento ponta a ponta no Cursor. Ele preserva os padrões bem-sucedidos do projeto CFQ - monorepositório, ingestão em camadas, contratos estáveis, jobs separados da API, migrações aditivas, gates e releases auditáveis - acrescentando isolamento institucional, cadeia de custódia, finalidade de acesso, gestão de casos e IA privada.

## Resultado esperado

1. Importar dados públicos e restritos com rastreabilidade.
2. Normalizar e cruzar dados fiscais, econômicos, cadastrais e patrimoniais.
3. Calcular potencial tributário com memória de cálculo.
4. Produzir indícios individualizados, nunca acusações automáticas.
5. Permitir validação humana e abertura de casos.
6. Acompanhar valor potencial, apurado, constituído, cobrado e recuperado.
7. Disponibilizar painéis executivos e operacionais por território, tributo e setor.

## Stack de referência

- Python 3.12, FastAPI, Pydantic e SQLAlchemy/Alembic.
- Angular e TypeScript para o portal.
- PostgreSQL transacional; BigQuery para analytics; Cloud Storage para arquivos.
- Cloud Run Services para API e web; Cloud Run Jobs para ingestões.
- Pub/Sub para eventos; Secret Manager e Cloud KMS.
- Terraform, Docker, GitHub Actions, OpenTelemetry, Prometheus/Grafana.
- Keycloak local; Identity Platform ou provedor OIDC homologado em produção.

## Começo rápido para o Cursor

1. Leia `AGENTS.md`.
2. Leia `current-state.yaml`.
3. Execute `prompts/00-bootstrap-audit.md` em modo de planejamento.
4. Execute `prompts/01-master-autonomous-loop.md`.
5. Implemente uma fase por vez, respeitando os gates em `docs/delivery/ROADMAP.md`.

## Release v0.3.0 - SIRTA Municipal

Esta release acrescenta o produto municipal, domínio do crédito, regra “nenhuma cobrança sem validação”, transferências intergovernamentais, prontidão IBS/CBS, contratos OpenAPI/AsyncAPI, schemas, checklists e plano de implementação em cinco sprints locais.

Depois da auditoria inicial, execute:

```text
@prompts/07-sirta-v03-implementation.md
```

Consulte `docs/delivery/SPRINT-PLAN-v0.3.md` e `docs/delivery/ROADMAP-SIRTA-2026.md`.

## Skills de engenharia curadas

Esta release contém onze skills de domínio, incluindo SIRTA, reconciliação de transferências e prontidão IBS/CBS, além de seis skills curadas da metodologia Superpowers: planejamento, TDD, debugging sistemático, solicitação e recebimento de review e verificação antes da conclusão. A ativação por fase está em `config/skills-policy.yaml` e `docs/delivery/SKILLS-BY-ROADMAP.md`.

As regras do projeto sempre têm precedência. Brainstorming, worktrees e execução paralela foram deliberadamente excluídos desta release.

Nenhum agente pode executar operações em nuvem, carregar dados reais, publicar uma versão ou alterar segurança sem autorização explícita.
