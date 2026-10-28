# Relatório final da homologação do Simulador SIRTA

Data: 28/10/2026. Ramo: `feat/professional-ui-v1`. Produção inalterada (web 0.4.23, API 0.3.124). Sem push, merge, deploy, ingestão ou alteração da carga de produção.

## 1. Conclusão

**Aprovação funcional condicionada.** O Simulador funciona como ferramenta de hipótese informada manualmente, com os testes executáveis aprovados. Ele **não está apto a usar dados públicos do SPED nem alíquotas como base fiscal**: nenhum indicador é CONFERIDO e nenhuma alíquota está homologada. A homologação definitiva depende de decisões humanas listadas na seção 8.

## 2. Resultados em números

| Medida | Resultado |
| --- | --- |
| Casos de teste planejados | 57 |
| Executados | 48 (84,2%) |
| Aprovados | 48 (100% dos executados; 84,2% dos planejados) |
| Reprovados | 0 |
| Não executados ou com lacuna | 9 (dependem de pessoa, dispositivo, autorização ou definição) |
| Requisitos (42) | 33 atendidos, 5 parciais, 4 não atendidos |
| pytest | 533 passaram, 8 falharam (preexistentes e sem relação), 1 ignorado, 542 coletados |
| Karma (web) | 218 de 218 (baseline 178) |
| `ng build` | Concluído |
| Migração 0111 | upgrade, downgrade e upgrade sem erro |
| Alíquotas homologadas | 0 de 31 |
| Indicadores CONFERIDO | 0 de 12 |

Detalhes: `SIMULADOR-CASOS-DE-TESTE.md`, `SIMULADOR-MATRIZ-REQUISITOS.md` e `evidence/ops/simulador-homologacao-20261028.txt`.

## 3. Funcionalidades aprováveis (aprovadas nos testes executados)

- Seleção de UF e município dependente (lista oficial do IBGE), impostos, operação, tipo de bem, quantidade e valor.
- Cálculo do imposto estimado ao centavo, com tratamento de vazio, zero, negativo, decimais e valores grandes.
- Gráfico da hipótese e atualização ao digitar.
- Rótulo "estimado" e aviso "não é imposto apurado nem devido".
- Transferências com direção própria e ICMS só por opção do usuário.
- Portão fechado por padrão para dados públicos, no web e na API.
- Acesso por sessão, território, finalidade e tenant, com auditoria e erros seguros.
- Cadastro de alíquotas que nunca marca homologação sem pessoa.

## 4. Reprovados

Nenhum caso executado foi reprovado ao final. Os defeitos abaixo foram reprovados em teste antes da correção.

## 5. Problemas encontrados e corrigidos

Cada item foi reproduzido por teste que falhava e corrigido em commit pequeno.

| # | Problema | Correção | Commit |
| --- | --- | --- | --- |
| 1 | O Simulador não tinha seletor de município (removido antes a pedido) | Seletor UF > município com lista do IBGE versionada e lida uma vez; resolução de alíquota por município | `4a2b9ab` |
| 2 | Erro de ponto flutuante no imposto (arredondamento ao centavo) | Aritmética limpa a 15 dígitos significativos | `875f389` |
| 3 | Valores enormes geravam infinito ou perda de precisão | Acima de 2^53 o imposto é recusado (nulo) | `875f389` |
| 4 | Imposto zero podia aparecer como "-R$ 0,00" | Zero negativo normalizado | `875f389` |
| 5 | Rótulos diziam "apurado", sugerindo imposto devido | Texto "estimado" e aviso de hipótese, com teste que impede "apurado" sem negação | `875f389` |
| 6 | Portão de dados públicos aceitava entradas nulas, cópias duplicadas e CONFERIDO sem evidência | Exige nível exatamente CONFERIDO, `publishableInSimulator === true` e evidência; avalia todas as cópias | `532045e` |
| 7 | Registro aceitava `conferred_at` no futuro | Registro recusa data futura | `532045e` |
| 8 | Leitura de alíquotas e recusa de uso fiscal sem evento de auditoria | `record_audit` na leitura e na recusa, com commit antes do erro | `384d166` |
| 9 | Homologação de alíquota não exigia restrições registradas nem revisão humana | Duas novas lacunas em `homologation_gaps` e CHECKs no banco (migração 0111) | `5071ee0` |

## 6. Indicadores ainda bloqueados

Todos os 12 indicadores do registro estão fora de CONFERIDO.

| Nível | Indicadores |
| --- | --- |
| NAO_CONFIAVEL (6) | Quantidade por UF, CFOP e ano; Compras por UF; valor estimado por UF, CFOP e ano; valor estimado por operação; transferências por direção; imposto do Simulador a partir de dados públicos |
| EXPLORATORIO (6) | Quantidade por UF e ano; quantidade nacional por CFOP e mês; valor nacional por CFOP e mês; alíquota do ICMS do Acre; alíquotas das demais UFs; ITCD, ITBI e ISS |

Motivos principais: falta a definição de `Quantidade NF-e`; as duas publicações do SPED divergem por CFOP e por entrada e saída; volumes incompatíveis com o porte de algumas UFs; entradas por transferência fora da planilha consolidada; CFOPs pendentes de definição oficial (ver `SIMULADOR-HOMOLOGACAO-DADOS.md`).

## 7. Situação das alíquotas

| Grupo | Situação |
| --- | --- |
| ICMS AC 19% (desde 01/04/2023) | Documentado com fonte primária (LC/AC 422/2022, `legis.ac.gov.br/detalhar/5461`) e exceções registradas. Falta revisão humana, conferência da lista completa de exceções e homologação. |
| ICMS AC 17% (2002 a 31/03/2023) | Fundamento informado, exceções não levantadas. Não homologada. |
| ICMS das outras 26 UFs | PENDENTE, lido de imagem, sem lei. |
| ITCD 6%, ITBI 3%, ISS 5% | Hipóteses de simulação; nunca homologáveis como alíquota única nacional. |
| Alíquotas municipais | Nenhuma cadastrada. |

Detalhes: `SIMULADOR-HOMOLOGACAO-JURIDICA.md` e `evidence/ops/aliquotas-homologacao-20261028.md`.

## 8. Pendências para a homologação definitiva

| ID | Pendência | Quem resolve |
| --- | --- | --- |
| P-01 | Obter do SPED a definição de `Quantidade NF-e` e da dimensão UF; conferir cada indicador e registrar responsável, data e evidência | Responsável pela conferência dos dados |
| P-02 | Definição oficial dos CFOPs 1.159, 2.159, 1.190, 2.170, 1.155 a 1.158, 5.154 e 5.157 | Responsável pela conferência dos dados |
| P-03 | Autorizar a carga das transferências recebidas (planilhas `.ods`) | Autoridade que autoriza |
| P-04 | Revisar e homologar o ICMS do Acre; conferir exceções, §§ 1º a 3º do art. 18 e cesta básica | Revisor jurídico |
| P-05 | Lei, vigência e URL de cada uma das 26 UFs; legislação de ITCD, ITBI e ISS | Revisor jurídico |
| P-06 | Conferir na fonte LC 204/2023, LC 227/2026, Resolução do Senado nº 9/1992 e LC 116/2003 | Revisor jurídico |
| P-07 | Definir o cálculo de "valor total" (preço unitário x quantidade) | Responsável funcional |
| P-08 | Testes com leitor de tela, navegadores e dispositivos reais; aceite por usuários | Responsável pela homologação funcional |
| P-09 | Autorizar publicação da API (aplica as migrações 0109, 0110 e 0111 na inicialização) e do web | Autoridade que autoriza |
| P-10 | Corrigir as 8 falhas preexistentes de pytest (4 em `test_alembic_paths.py`, 1 em `test_official_ingest.py`, 3 em `test_source_ingest.py`) e os 13 apontamentos de lint e formatação preexistentes | Equipe técnica |

## 9. Critérios de saída não atendidos

- Indicadores CONFERIDO por responsável identificado (P-01).
- Alíquotas homologadas por revisor identificado (P-04 a P-06).
- Acessibilidade com leitor de tela e testes em dispositivos reais (P-08).
- Autorização para publicar (P-09).

## 10. Riscos residuais

- A migração 0109 a 0111 ainda não foi aplicada em produção. A publicação da API depende de autorização e as 4 falhas de `test_alembic_paths.py` (subir do zero em banco vazio) são preexistentes e devem ser entendidas antes de qualquer publicação que dependa desse caminho.
- Publicar o web sem a API ou a API sem o web não foi testado em ambiente integrado.
- Exceção por mercadoria e operação interestadual não são modeladas; o Simulador usa só a alíquota modal.

## 11. Recomendação

1. **Aprovar funcionalmente, com condições**, o Simulador em modo de hipótese manual, em ambiente de homologação ou piloto controlado. Em todo o uso, o resultado deve ser chamado de estimativa.
2. **Não** liberar o uso de dados públicos do SPED nem de alíquotas como referência fiscal enquanto nenhum indicador for CONFERIDO e nenhuma alíquota estiver homologada. O portão fechado cumpre esse bloqueio por padrão.
3. **Não** fazer deploy nem alterar a carga de produção antes das autorizações P-03 e P-09 e do entendimento das falhas de P-10.
4. Fazer a homologação jurídica (P-04 a P-06) em paralelo, começando pelo ICMS do Acre, que já tem fonte primária e exceções registradas.
5. Registrar a decisão no modelo `SIMULADOR-ATA-HOMOLOGACAO.md`, preenchido por pessoas identificadas.

Fundamento: 48 de 48 casos executados aprovados, nenhuma regressão (as 8 falhas já existiam), e todos os caminhos que poderiam apresentar um número não conferido como fiscal estão fechados e testados. A recomendação não implica aprovação humana: a ata permanece em branco.

## 12. Atualização de 28/10/2026 (após a decisão do responsável)

- Decisões do responsável: Quantidade NF-e definida como quantidade de itens (sem confirmação do SPED) e percentuais de ICMS das UFs, ITCD, ITBI e ISS valendo como estão, só como parâmetro do Simulador. Nada foi promovido a CONFERIDO nem homologado; a ata continua em branco.
- Publicação autorizada pelo usuário: API 0.3.125 e web 0.4.24, com as migrações 0109 a 0111 aplicadas na partida. Evidência: evidence/ops/prod-simulador-0.4.24-20261028.txt. O item P-09 (publicação) está atendido; P-01, P-04 a P-06 e P-08 continuam abertos.
- Em produção o Simulador opera só com hipóteses manuais. A conferência com sessão autenticada ainda precisa ser feita por um operador.
- O rollback da API exige antes lembic downgrade 0108_sped_operations em tarefa pontual autorizada.
