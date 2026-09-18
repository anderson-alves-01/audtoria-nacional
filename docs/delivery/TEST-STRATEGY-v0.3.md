# Estratégia de testes v0.3

## Domínio

- RED-GREEN-REFACTOR para estados e comandos.
- Tabela de todas as transições permitidas e negadas.
- Propriedades: crédito bloqueado nunca inicia cobrança; evento sempre acompanha transição bem-sucedida.

## Autorização

- Tenant correto/incorreto.
- Território permitido/negado.
- Finalidade presente, expirada e ausente.
- Papel suficiente/insuficiente.
- Segregação criador versus validador.

## API

- OpenAPI lint e compatibilidade.
- Problem details para 403, 409 e 422.
- Paginação e ordenação determinística.
- Idempotency-Key em comandos críticos.

## Dados

- Fixtures sintéticas.
- Schema, contagens e reconciliação.
- Quarentena.
- Reexecução sem duplicidade.
- Rollback lógico.

## Frontend

- Estados de loading, vazio, erro e dados parciais.
- Acessibilidade WCAG 2.2 AA.
- Diferença visual entre potencial, finding, validado e recuperado.
- E2E da identificação até tentativa bloqueada e validação até cobrança permitida.

## Segurança

- Secret scan e dependency scan.
- Logs sem CPF/CNPJ completo, tokens ou documentos.
- Testes IDOR e cross-tenant.
- Exportação não implementada na v0.3 ou bloqueada por padrão.

