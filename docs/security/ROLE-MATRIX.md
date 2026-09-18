# Matriz de papéis e segregação

| Ação | Analista | Validador | Cobrança | Dívida ativa | Procuradoria | Controle interno | Admin |
|---|---:|---:|---:|---:|---:|---:|---:|
| Consultar carteira autorizada | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | condicionado |
| Criar finding | ✓ | ✓ | - | - | - | - | - |
| Validar crédito | - | ✓ | - | - | - | - | - |
| Iniciar cobrança | - | - | ✓ | - | - | - | - |
| Registrar parcelamento | - | - | ✓ | ✓ | - | - | - |
| Propor inscrição | - | - | - | ✓ | - | - | - |
| Aprovar encaminhamento jurídico | - | - | - | ✓ | ✓ | - | - |
| Auditar eventos | leitura própria | leitura própria | leitura própria | leitura própria | autorizado | ✓ | técnico |
| Administrar identidade | - | - | - | - | - | auditoria | ✓ |

Regras:

- Criador do finding não aprova sozinho o crédito correspondente.
- Administrador técnico não recebe acesso ao conteúdo fiscal por padrão.
- Acesso emergencial é temporário, justificado e auditado.
- Exportação exige reautenticação e política explícita.
- Permissão de interface nunca substitui autorização da API.

