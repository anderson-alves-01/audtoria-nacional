# Relatório: transferências por direção, ICMS do Acre e alíquotas por localidade

Data: 2026-10-28. Estado: tudo local, nada publicado. Produção segue com web 0.4.23 (`sirta-prod-web:31`) e API 0.3.124 (`sirta-prod-api:30`). Nenhum deploy, push ou ingestão foi feito. A carga `d25c890e-f93c-4b64-b307-247d64799e3f` continua `published=false`, `homologated=false`, `createsTaxCredit=false`.

Este relatório complementa `docs/delivery/RELATORIO-SIMULADOR-SIRTA-20261028.md` e aplica as três decisões metodológicas do responsável.

## 1. Funcionalidades implementadas

### 1.1 Transferências por direção
- `domain/sped_operations.py`: tabela de CFOP baseada na tabela oficial (Sefaz-PE, `cfop.htm`, lida em 2026-10-28) e `classify_cfop_sirta`, que devolve operação, direção (`RECEBIDA` ou `REMETIDA`) e estado (`CONFIRMADA`, `PENDENTE_CLASSIFICACAO` ou `EXCLUIDA`). A regra publicada na planilha (`classify_cfop`) continua intacta, porque a auditoria e a reconciliação a usam.
- Confirmadas na tabela oficial: recebidas 1.151 a 1.154 e 2.151 a 2.154; remetidas 5.151, 5.152, 5.153, 5.155, 5.156 e 6.151, 6.152, 6.153, 6.155, 6.156. A premissa do responsável sobre 1.151 e 1.152 está confirmada.
- Pendentes de classificação: 1.155 a 1.159, 2.155 a 2.159, 1.190, 2.170 e, nas saídas, 5/6/7.151 a .199 que a tabela não lista. A tabela consultada não define esses códigos. **1.159 e 2.159 não foram tratados como transferência por analogia ao prefixo 15x.**
- Migração aditiva `0110_direction_rate_scope`: coluna nula `direcao` em `sped_operation_facts`. As linhas de "Transferências" já carregadas (todas saídas) ficam `REMETIDA`. Nada foi reescrito nem apagado.
- API, só campos novos: `direcao` nos itens de Transferências, `classificacaoCfop` no nível CFOP, e `transferQuantity` e `transferUnconfirmedQuantity` na reconciliação. A reconciliação ganhou um aviso quando há volume fora da tabela oficial.
- As direções nunca são somadas: `assert_single_direction` recusa a mistura no domínio e `sped-logic.ts` deixa em branco a célula que misturar RECEBIDA e REMETIDA.
- Novo indicador `sped_transferencias_por_direcao` (NAO_CONFIAVEL), que entra no portão dos dados públicos da API e da web.

### 1.2 Simulador
- Operação "Transferências" mostra o seletor de direção (recebidas, remetidas). Sem direção escolhida, nenhum dado público de transferência entra (falha fechada). Trocar de operação zera a direção e o opt-in.
- ICMS não é calculado numa transferência por padrão. A tela explica o motivo (LC 204/2023, informada pelo responsável, a conferir). O cálculo só ocorre pelo opt-in "Calcular ICMS mesmo assim (hipótese: equiparação optada)", rotulado como hipótese.

### 1.3 ICMS do Acre
- Migração `0110`: `official_url`, `legal_basis` e vigências do AC.
  - 19%: LC/AC 55/1997 art. 18, I, redação da LC/AC 422/2022, vigência 01/04/2023. Página: `https://sefaz.ac.gov.br/2021/?p=11479`.
  - 17%: redação da LC/AC 100/2001, vigência de 01/01/2002 a 31/03/2023, conferida no texto consolidado da LC 55/1997. Página: `https://sefaz.ac.gov.br/2021/?p=12159`. A vigência inicial antes desconhecida agora está preenchida.
- Os endereços são das páginas da Sefaz/AC que encontrei (escolha do responsável). A mensagem citava `legis.ac.gov.br` sem os endereços. O responsável confere antes de homologar.
- Novo passo humano separado: `homologated_by` e `homologated_at` (nulos). `homologation_gaps` passou a exigir `homologated_by`. As duas linhas do AC têm a documentação jurídica completa e **continuam não homologadas**, faltando só o revisor e a conferência das condições de aplicação (exceções por mercadoria).

### 1.4 Cadastro de alíquotas por localidade
- `tax_rate_versions` ganhou `jurisdiction_level` (`UF`, `MUNICIPIO`, `SIMULACAO`), `municipality_ibge_code`, `operation_ref`, `reference_min` e `reference_max`. O índice único passou a considerar localidade e operação. Restrições: linha `SIMULACAO` só pode ser PENDENTE, linha `MUNICIPIO` exige código IBGE, homologada exige VALIDADO e a faixa de referência deve ser coerente.
- ITCD (estadual), ITBI e ISS (municipais): 6%, 3% e 5% viraram linhas `SIMULACAO`, rotuladas "parâmetro de simulação, não é alíquota de UF nem de município". Limites de referência: ITCD até 8% e ISS de 2% a 5%, registrados como informados pelo responsável, a conferir na fonte.
- O resolvedor (`domain/tax_rates.py` e `resolveRate` no web) casa ITBI e ISS só por município, ITCD e ICMS por UF, e nunca devolve um parâmetro de simulação como alíquota de jurisdição. Uma linha de jurisdição real vence o parâmetro. Uma alíquota ligada a uma operação só vale quando essa operação é pedida.
- Sem seletor de município no Simulador: foi removido a pedido e ainda não há dado por município.

## 2. Resultados

### 2.1 Reaplicação às 1.041 células (`evidence/ops/sped-auditoria-omissoes-20261028.md`, seções 10 e 11)

| Grupo SIRTA | Células | NF-e | Parcela |
|---|---:|---:|---:|
| Transferência recebida confirmada | 844 | 132.237.096 | 49,3% |
| Pendente de classificação | 197 | 136.080.849 | 50,7% |
| Total | 1.041 | 268.317.945 | 100,0% |

- Pendentes principais: 1.159 (80.968.068) e 2.159 (55.094.683).
- Na planilha, 38.882.859 NF-e (10,2%) das 380.140.367 "Transferências" estão em CFOPs que a tabela não lista como transferência (5.159 com 18,4 milhões, 5.160, 6.159, 5.192, 6.162 e outros). O indicador publicado fica ressalvado.
- A classe pela regra publicada (1.041 indevidas, 268.317.945 NF-e) não mudou: a nova classificação é uma camada adicional, sem alterar originais nem contagens.

### 2.2 Alíquotas (`evidence/ops/aliquotas-homologacao-20261028.md`)
- 31 versões, **0 homologadas**. AC: única lacuna é "homologação pelo responsável". 26 UFs: todas as lacunas. ITCD, ITBI e ISS: lacuna "alíquota da jurisdição" além das demais.

## 3. Testes executados

| Verificação | Resultado |
|---|---|
| `pytest` completo | 470 passaram, 1 ignorado, 8 falharam |
| As 8 falhas | as mesmas de antes, sem relação com esta mudança: 4 em `tests/integration/test_alembic_paths.py` (tabela `gold_finance_state_summaries` já existe) e 4 em `test_source_ingest.py` e `test_official_ingest.py` |
| Novos e alterados (Python) | `test_cfop_transfers.py`, `test_tax_rates.py`, `test_tax_rates_audit.py`, `test_sped_omission_audit.py`, `test_indicator_reliability.py`, `test_tax_rates_api.py` (restrições do cadastro, AC, SIMULACAO, município e operação), `test_sped_api.py` (direção e classificação por CFOP) |
| Migração `0110` | `upgrade head`, `downgrade 0109` e `upgrade head` de novo no banco local de teste, sem erro |
| `ruff check` e `ruff format` | limpos nos arquivos alterados. O `ruff check .` do repositório inteiro acusa erros antigos em `tools/ops/prod-*` e outros, fora desta mudança |
| `ng test` | 178 de 178 passaram |
| `ng build` | concluído sem erro |
| OpenAPI | YAML válido e `tests/contract` passando |

Evidência: `evidence/ops/transferencias-aliquotas-20261028.txt`.

## 4. Bloqueios restantes
- Os CFOPs 1.159, 2.159, 1.190, 2.170 e os 5/6/7.15x a .19x fora da tabela não têm significado oficial confirmado. A tabela da Sefaz-PE consultada não os lista.
- As transferências recebidas existem só nos `.ods` originais. Carregá-las no banco é ingestão real e exige autorização explícita.
- Não há regra de deduplicação nem identificação de documentos, então não existe contagem distinta de transferências.
- Nenhuma alíquota está homologada. O AC aguarda revisor. As outras 26 UFs aguardam lei, vigência, URL e responsável.
- Não há legislação cadastrada de ITCD por UF, nem de ITBI e ISS por município.
- LC 204/2023, LC 227/2026, Resolução do Senado 9/1992 e LC 116/2003 foram registradas como informadas pelo responsável. Não foram conferidas na fonte nesta entrega.
- Publicar a API aplica as migrações `0109` e `0110` na inicialização, e publicar o web remove a seção de dados públicos do Simulador em produção. Ambos aguardam autorização.

## 5. Informações necessárias
- Fonte oficial do significado de 1.159, 2.159, 1.190 e 2.170 e dos CFOPs 5/6/7.15x a .19x fora da tabela.
- Autorização (ou não) para carregar as transferências recebidas dos `.ods`.
- Revisor responsável pela homologação do ICMS do AC, e confirmação dos endereços da Sefaz/AC ou envio dos de `legis.ac.gov.br`.
- Para ITCD: lei, alíquota, faixas, base e vigência de cada UF. Para ITBI: lei do município, alíquota, base e vigência. Para ISS: lei do município, item da lista de serviços, alíquota e vigência.
- Conferência na fonte das referências legais informadas (LC 204/2023, LC 227/2026, Resolução do Senado 9/1992, LC 116/2003).

## 6. Rollback
- Migração: `alembic downgrade 0109_tax_rate_versions` remove colunas, restrições e o índice novo e recria o índice anterior. Os dados do AC atualizados e os valores de `note` não são revertidos (a atualização só preenche documentação). Se existirem linhas municipais, o `downgrade` pode falhar no índice antigo: remova-as antes, com operação registrada.
- Código: `git revert` dos commits desta entrega. Nada foi publicado.
