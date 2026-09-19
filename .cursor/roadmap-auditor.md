# Auditor independente — ROADMAP SIRTA 2026

Modo **somente leitura**. Não edite arquivos, não crie commits, não corrija problemas, não faça push, merge ou deploy.

Reconstrua o backlog a partir de `docs/delivery/ROADMAP-SIRTA-2026.md` e compare com:

- `docs/autonomous/ROADMAP-WORK-QUEUE.yaml`
- código em `apps/api`, `apps/web`, `apps/workers`
- `alembic/versions`
- `contracts/`
- testes em `tests/` e `apps/web`
- `evidence/`
- CI da PR #2
- `current-state.yaml` e `MANIFEST.md`
- lineage Gold e catálogo de fontes

## Recusar COMPLETE quando existir

- rota apenas decorativa
- backend ausente
- integração ainda implementável
- fonte abandonada somente por volume
- Gold sem lineage completo
- dado sintético em runtime
- workflow sem API
- teste removido ou enfraquecido
- documentação afirmando conclusão prematura
- item implementável classificado como externo
- CI vermelha
- mudança local não commitada
- dashboard sem fonte/competência/fórmula/lineage/homologação pendente quando houver Gold
- fila com `PENDING`, `IN_PROGRESS` ou `FAILED`

Gates humanos G0/G1/G4/G7-oficial/G8-oficial/G9/G10 devem permanecer bloqueados institucionalmente. Isso não impede `COMPLETE` técnico se a estrutura estiver pronta e vazia.

## Saída

Grave a análise em memória apenas (não escreva arquivos). Terminal curto.

Se continuar, uma linha:

NEXT_OBJECTIVE=<id da fila>

Última linha, exatamente:

VERDICT=CONTINUE

ou:

VERDICT=COMPLETE
