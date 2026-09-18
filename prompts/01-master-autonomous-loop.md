# Prompt mestre de desenvolvimento autônomo

Implemente a Plataforma Auditoria Nacional de ponta a ponta seguindo o roadmap, com mínima intervenção humana.

## Loop

Enquanto existir trabalho não bloqueado:

1. Leia a fonte de verdade e selecione a próxima história pronta.
2. Escreva plano curto, riscos e critérios de aceite.
3. Implemente uma fatia vertical pequena.
4. Rode todos os testes e gates aplicáveis.
5. Corrija falhas de causa conhecida e repita os testes.
6. Revise segurança, privacidade, contratos, observabilidade e documentação.
7. Registre evidências e atualize `current-state.yaml`.
8. Faça commit atômico somente quando autorizado pelo ambiente.
9. Continue para a próxima história.

## Política de parada

Pare e solicite decisão humana somente para: credenciais, acesso a dados reais, interpretação jurídica/tributária, mudança destrutiva, custo relevante, publicação externa, deploy em produção ou requisito materialmente ambíguo.

Não simule que um bloqueio foi resolvido. Não reduza testes. Não invente dados, fontes ou validações.

