# Matriz de requisitos do Simulador SIRTA

Data: 28/10/2026. Estados: ATENDIDO (implementado e testado), PARCIAL (implementado com limite declarado) e NÃO ATENDIDO (bloqueado por decisão ou informação externa). "Validado" quer dizer que há teste executado e aprovado, nunca que um responsável humano homologou. Os IDs de casos de teste (CT) estão em `SIMULADOR-CASOS-DE-TESTE.md`.

## 1. Funcionais

| ID | Requisito | Implementação | Teste | Evidência | Estado |
| --- | --- | --- | --- | --- | --- |
| RQ-01 | Menu "Simulador" acima de Visão geral | `apps/web/src/app/app.routes.ts` e menu | CT-018 | Karma 218/218 | ATENDIDO |
| RQ-02 | Selecionar UF | `simulador-page.component.{ts,html}` (`data-testid="uf"`) | CT-001, CT-002 | Karma | ATENDIDO |
| RQ-03 | Selecionar município dependente da UF | `simulador-municipios.ts`, `apps/web/public/ibge-municipios.json` (5.571 municípios, 27 UFs) | CT-002, CT-003, CT-043 | `evidence/ops/ibge-municipios-20261028.txt` | ATENDIDO |
| RQ-04 | Selecionar impostos (ICMS, ITCD, ITBI, ISS) | `simulador-aliquotas.ts` | CT-001 | Karma | ATENDIDO |
| RQ-05 | Selecionar operação e tipo de bem | `simulador-page.component.ts` | CT-001 | Karma | ATENDIDO |
| RQ-06 | Informar quantidade e valor | `simulador-page.component.html` | CT-001, CT-004, CT-005, CT-006 | Karma | ATENDIDO |
| RQ-07 | Valor total | O valor informado é tratado como total | CT-064 | Sem teste de preço unitário x quantidade | PARCIAL (requisito sem definição) |
| RQ-08 | Calcular imposto hipotético ao centavo | `simulador-logic.ts` (`taxAmount`) | CT-007 | Karma | ATENDIDO |
| RQ-09 | Gráfico atualiza com o valor | `simulador-logic.ts` (`hypothesisChart`) | CT-012 | Karma | ATENDIDO |
| RQ-10 | Tratar nulo, zero, negativo, grande e decimal | `simulador-logic.ts` | CT-004 a CT-007 | Karma | ATENDIDO |
| RQ-11 | Funcionar em tela estreita | `simulador-page.component.scss` | CT-015 | Karma (viewport simulado) | PARCIAL (sem dispositivo físico, CT-061) |
| RQ-12 | Acessibilidade | Rótulos por controle | CT-016 | Karma | PARCIAL (sem leitor de tela, CT-060) |
| RQ-13 | Resultado sempre rotulado como hipótese | Rótulos "estimado" e aviso na página | CT-014 | Karma | ATENDIDO |
| RQ-14 | Transferências: direção e ICMS opcional | `simulador-logic.ts`, `domain/sped_operations.py` | CT-011, CT-040 | Karma e pytest | ATENDIDO |
| RQ-15 | Abrir o Simulador a partir do painel SPED | `applyQuery` | CT-017 | Karma | ATENDIDO |

## 2. Dados e confiabilidade

| ID | Requisito | Implementação | Teste | Evidência | Estado |
| --- | --- | --- | --- | --- | --- |
| RQ-20 | Três níveis NAO_CONFIAVEL, EXPLORATORIO e CONFERIDO | `domain/indicator_reliability.py`, `config/indicator-reliability.yaml` | CT-024 a CT-029 | pytest | ATENDIDO |
| RQ-21 | Só CONFERIDO alimenta cálculo fiscal ou publicação | `application/indicator_reliability.py` (`authorize_fiscal_use`), `shared/reliability/indicator-reliability.ts` | CT-020 a CT-027 | pytest e Karma | ATENDIDO |
| RQ-22 | CONFERIDO exige responsável, data e evidência; data futura é recusada | `parse_registry` | CT-028 | pytest | ATENDIDO |
| RQ-23 | Falhar fechado (bloco ausente, registro quebrado, leitura com erro) | web e API | CT-021, CT-022, CT-027 | pytest e Karma | ATENDIDO |
| RQ-24 | Nenhuma promoção automática | Sem código de promoção | CT-037 | pytest | ATENDIDO |
| RQ-25 | Indicadores do SPED conferidos por humano | Registro: 0 CONFERIDO (6 NAO_CONFIAVEL, 6 EXPLORATORIO) | CT-063 | `config/indicator-reliability.yaml` | NÃO ATENDIDO (decisão humana) |
| RQ-26 | 46.825 registros do SPED reproduzem os originais | `tools/ops/sped-source-reconcile.py` | CT-042 | `evidence/ops/sped-homologacao-reconciliacao-20261028.md` | ATENDIDO |
| RQ-27 | 1.041 omissões classificadas (844 recebidas confirmadas e 197 pendentes) | `tools/ops/sped-omission-audit.py` | CT-042 | Mesma evidência | ATENDIDO |
| RQ-28 | CFOP classificado só por fonte oficial; o restante PENDENTE | `classify_cfop_sirta` | CT-040 | pytest (36) | ATENDIDO |
| RQ-29 | Direções RECEBIDA e REMETIDA nunca somadas | `assert_single_direction` | CT-011, CT-040 | pytest e Karma | ATENDIDO |
| RQ-30 | Carga das transferências recebidas | Dados só nas planilhas `.ods` | CT-065 | Sem carga | NÃO ATENDIDO (aguarda autorização) |
| RQ-31 | Definição de `Quantidade NF-e` | Não existe nas fontes | CT-063 | `SIMULADOR-HOMOLOGACAO-DADOS.md` | NÃO ATENDIDO (informação externa) |

## 3. Alíquotas e legislação

| ID | Requisito | Implementação | Teste | Evidência | Estado |
| --- | --- | --- | --- | --- | --- |
| RQ-40 | Cadastro de alíquotas com fundamento, URL, vigência, status e restrições | `tax_rate_versions`, migrações 0109 a 0111 | CT-050, CT-053 | pytest | ATENDIDO |
| RQ-41 | Homologação só por pessoa (`homologated_by`) e só após revisão | `homologation_gaps`, CHECKs do banco | CT-050, CT-053 | pytest | ATENDIDO |
| RQ-42 | ICMS do Acre: 19% desde 01/04/2023, fonte primária e exceções | Migração 0111 | CT-051 | `SIMULADOR-HOMOLOGACAO-JURIDICA.md` | PARCIAL (documentado, não homologado) |
| RQ-43 | ICMS das demais 26 UFs | 26 linhas PENDENTE, lidas de imagem | CT-055 | `evidence/ops/aliquotas-homologacao-20261028.md` | NÃO ATENDIDO (sem lei) |
| RQ-44 | ITCD, ITBI e ISS (6%, 3%, 5%) como hipótese | Nível SIMULACAO, nunca VALIDADO | CT-052 | pytest | ATENDIDO (como hipótese) |
| RQ-45 | Alíquota por município (ITBI e ISS) | Resolução por município pronta, nenhuma linha cadastrada | CT-054, CT-068 | Karma e pytest | PARCIAL |
| RQ-46 | Alíquota nunca apresentada como homologada sem homologação | `homologated` calculado na API; rótulo no web | CT-010, CT-050 | pytest e Karma | ATENDIDO |

## 4. Segurança e governança

| ID | Requisito | Implementação | Teste | Evidência | Estado |
| --- | --- | --- | --- | --- | --- |
| RQ-60 | Autenticação em toda rota | `Depends(get_access_context)` | CT-030 | pytest | ATENDIDO |
| RQ-61 | RBAC e ABAC por tenant, território e finalidade | `AccessContext` | CT-031 a CT-033 | pytest | ATENDIDO |
| RQ-62 | Erros sem vazamento | Handlers `problem+json` | CT-034 | pytest | ATENDIDO |
| RQ-63 | Auditoria de acessos e recusas | `record_audit` em `tax_rates.list` e `authorize_fiscal_use` | CT-035, CT-036 | pytest | ATENDIDO |
| RQ-64 | Segregação de ambientes e ausência de segredo no Git | `.gitignore`, `.env.example` | CT-038 | pytest | ATENDIDO |
| RQ-65 | Sem crédito tributário | `createsTaxCredit: false` nas respostas | CT-037, CT-041, CT-050 | pytest (`test_sped_api.py`, `test_tax_rates_api.py`) | ATENDIDO |
| RQ-66 | Migrações aditivas e reversíveis | `0111_tax_rate_review_fields.py` | CT-056 | `evidence/ops/simulador-homologacao-20261028.txt` | ATENDIDO |
| RQ-67 | Dados reais proibidos em testes | Fixtures sintéticas; leitura dos originais é somente leitura | CT-041, CT-042 | pytest | ATENDIDO |

## 5. Resumo (42 requisitos)

| Estado | Quantidade |
| --- | --- |
| ATENDIDO | 33 |
| PARCIAL | 5 (RQ-07, RQ-11, RQ-12, RQ-42, RQ-45) |
| NÃO ATENDIDO | 4 (RQ-25, RQ-30, RQ-31, RQ-43) |

Os requisitos não atendidos dependem de decisão humana, autorização ou informação externa. Nenhum foi contornado.
