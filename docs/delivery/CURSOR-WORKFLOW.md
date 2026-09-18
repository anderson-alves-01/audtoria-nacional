# Operação do Cursor

## Ordem de uso

1. `@prompts/00-bootstrap-audit.md`
2. Revisar o plano proposto.
3. `@prompts/01-master-autonomous-loop.md`
4. Para uma feature específica, usar `@prompts/02-implement-feature.md`.
5. Para carga, usar `@prompts/03-data-pipeline.md`.
6. Antes de release, executar revisão de segurança e release.
7. Encerrar a sessão com o handoff.

## Coordenação das skills

O Orchestrator mantém o plano e chama Product Architect, Data Engineer, Backend, Frontend, Security, DevOps e QA. Uma skill não aprova o próprio trabalho crítico: segurança e release são verificações independentes.

## Autonomia permitida

O Cursor pode criar código, testes, documentação, fixtures sintéticas, containers locais e planos de infraestrutura. Pode corrigir automaticamente falhas locais cuja causa esteja comprovada.

## Autonomia proibida

Não pode usar credenciais, consultar bases restritas, executar carga real, criar recursos pagos, alterar IAM, publicar externamente, fazer deploy de produção ou aceitar interpretação jurídico-tributária sem decisão humana.

## Regra de looping

O loop continua enquanto houver uma tarefa pronta e todos os requisitos estiverem disponíveis. Ao falhar, o agente diagnostica, corrige e testa novamente. Após três tentativas com a mesma causa não resolvida, registra evidências, reduz o problema e solicita intervenção, sem mascarar o erro.

