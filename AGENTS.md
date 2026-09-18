# Instruções permanentes para agentes

## Missão

Construir a Plataforma Auditoria Nacional de ponta a ponta, com entregas incrementais, comprováveis, seguras e reversíveis.

O produto corrente é o SIRTA Municipal. Antes de alterar comportamento de crédito, transferência ou IBS/CBS, carregue a skill específica e os contratos correspondentes.

## Fonte de verdade

Ordem obrigatória:

1. Código e histórico Git.
2. `current-state.yaml`.
3. ADRs em `docs/architecture/`.
4. Contratos em `contracts/`.
5. `docs/delivery/ROADMAP-SIRTA-2026.md` e `SPRINT-PLAN-v0.3.md`.
6. Política em `config/skills-policy.yaml`.
7. Backlog.
8. Evidências de testes e releases.

Não inferir estado concluído apenas por comentários, nomes de branches ou documentação antiga.

## Regras inegociáveis

- Planejar antes de editar.
- Fazer mudanças pequenas e coerentes.
- Não usar `git add .`.
- Não sobrescrever mudanças do usuário.
- Não apagar dados, buckets, datasets, tabelas ou ambientes.
- Não executar ingestão real sem autorização explícita.
- Não repetir snapshot ou carga já concluída.
- Usar migrations exclusivamente aditivas; remoções exigem ciclo de depreciação.
- Preservar compatibilidade de endpoints e tabelas Gold.
- Todo job deve ser idempotente, retomável e rastreável por `run_id`.
- Toda carga deve registrar origem, checksum, competência, esquema, finalidade e contagens.
- Falhar fechado em caso de território, tenant, finalidade ou autorização ausente.
- Dados reais são proibidos em local, desenvolvimento e testes.
- IA não decide, acusa, autua ou publica. Ela recomenda e cita evidências.
- Não enviar dados sigilosos a modelos públicos.
- Toda ação sensível gera evento de auditoria imutável.
- Scripts destrutivos precisam de dry-run, escopo explícito e dupla confirmação.

## Ciclo obrigatório por tarefa

1. Reproduzir ou definir o comportamento atual.
2. Identificar requisitos e riscos.
3. Atualizar plano e critérios de aceite.
4. Implementar a menor fatia vertical.
5. Executar lint, testes unitários, integração, contratos e segurança aplicáveis.
6. Validar migrations e SQL antes de execução.
7. Atualizar documentação e `current-state.yaml`.
8. Salvar evidências em `evidence/`.
9. Parar no gate quando houver dependência humana ou institucional.

## Skills de engenharia

Use somente as skills de engenharia incluídas nesta release. A ativação e os parâmetros são definidos em `config/skills-policy.yaml`. Em caso de conflito, este arquivo, o estado atual, os ADRs, os contratos e as regras do projeto têm precedência. Skills excluídas não podem ser instaladas ou chamadas implicitamente.

## Definition of Done

Uma história só termina quando:

- critérios de aceite estão comprovados;
- testes relevantes passam;
- contratos continuam compatíveis;
- logs não expõem dados sensíveis;
- observabilidade foi adicionada;
- rollback foi descrito;
- documentação e estado foram atualizados;
- não existem placeholders silenciosos, mocks em produção ou erros ignorados.

## Proibições de atalho

- Não marcar tarefa como concluída apenas porque compila.
- Não substituir integração real por mock sem registrar dívida técnica.
- Não criar números de potencial sem fórmula e fontes.
- Não publicar dados com status `UNVALIDATED`, `QUARANTINED` ou `REJECTED`.
- Não fazer correção manual de produção sem migration ou registro de operação.
