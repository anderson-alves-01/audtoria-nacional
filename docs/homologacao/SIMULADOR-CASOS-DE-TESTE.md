# Casos de teste do Simulador SIRTA

Execução de 28/10/2026, ramo `feat/professional-ui-v1`, banco sintético local. A coluna "Observado" registra só o que foi de fato executado. Comandos e saídas: `evidence/ops/simulador-homologacao-20261028.txt`.

Legenda do estado: APROVADO (executado e passou), NÃO EXECUTADO (depende de pessoa, dispositivo ou autorização) e LACUNA (requisito sem definição que permita testar).

Abreviações: `PG` = `apps/web/src/app/simulador/simulador-page.component.spec.ts`, `LG` = `simulador-logic.spec.ts`, `MU` = `simulador-municipios.spec.ts`, `GT` = `apps/web/src/app/shared/reliability/indicator-reliability.spec.ts`. Os testes Python estão em `tests/`.

## 1. Formulário e cálculo (web)

| ID | Caso | Pré-condição | Procedimento | Resultado esperado | Observado | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CT-001 | Campos e opções do requisito | Simulador aberto | Percorrer UF, município, impostos (ICMS, ITCD, ITBI, ISS), operações, tipos de bem, quantidade e valor | Todas as opções do requisito existem e são preenchíveis | Passou | PG `offers the requested taxes, operations and goods types`; PG `walks the whole form: UF, municipality, taxes, operation, goods, quantity and value` | APROVADO |
| CT-002 | Seletor UF > município | Lista do IBGE carregada | Escolher UF, depois município; trocar a UF | Só municípios da UF, em ordem alfabética; trocar a UF zera o município; código de outra UF é recusado; lista lida uma vez | Passou | PG `lists only the municipalities of the chosen UF, in alphabetical order`, `reads the list once, even when the UF changes`, `clears the municipality when the UF changes and refuses a code from another UF`, `does not read the municipality list until a UF is chosen`; MU (4 testes) | APROVADO |
| CT-003 | Falha na leitura da lista de municípios | Leitura da lista falha | Escolher UF | Simulador segue por UF e informa o erro | Passou | PG `keeps working by UF when the municipality list cannot be read` | APROVADO |
| CT-004 | Precisão decimal, zero e vazio | Campos vazios | Digitar valor com decimais; digitar zero; esvaziar | Decimais preservados; zero é zero (não ausente); vazio não mostra imposto | Passou | PG `keeps decimal precision typed in the field`, `shows nothing for an empty field and treats zero as zero, not as missing` | APROVADO |
| CT-005 | Entradas inválidas | Campos vazios | Digitar negativo, expoente, texto e valores absurdos | Entrada ignorada, aviso ao usuário, nenhum imposto calculado | Passou | PG `ignores negative, exponent and absurd entries and says so, without computing a tax`, `ignores a negative input instead of simulating with it` | APROVADO |
| CT-006 | Valores muito grandes | Campos vazios | Digitar quantidades e valores enormes | Sem notação científica e sem infinito; acima de 2^53 o imposto é recusado | Passou | PG `handles very large quantities and values without scientific notation or infinity`; LG `handles large values exactly to the cent and refuses what a double cannot hold`, `compares large quantities without precision loss up to 2^53` | APROVADO |
| CT-007 | Imposto estimado ao centavo | Alíquota conhecida | Calcular valor x alíquota | Meio arredonda para cima ao centavo, sem erro de ponto flutuante; zero sem sinal negativo; alíquota zero dá imposto zero | Passou | LG `rounds half up to the cent without binary floating-point error`, `matches exact decimal arithmetic over a sweep of values and rates`, `returns zero tax for a zero value and never a negative zero`, `keeps a rate of zero as a zero tax, not as a missing one`, `rejects negative, infinite and not-a-number inputs`, `keeps tiny and fractional values without turning them into zero by accident`, `multiplies value by rate to the cent and keeps missing as null` | APROVADO |
| CT-008 | ICMS sem UF | Nenhuma UF | Marcar ICMS sem escolher UF | ICMS fica vazio e há aviso | Passou | PG `leaves ICMS empty and warns when no UF is chosen` | APROVADO |
| CT-009 | ICMS do Acre por ano | UF = AC | Ver 2022 a 2025 | 17% antes de 01/04/2023, 19% depois; o ano da mudança fica vazio porque a alíquota mudou | Passou | LG `uses the Acre rate in force in each year and leaves the year of the change empty`, `uses the Acre rate of each year in the table and in the scenario`; PG `leaves the 2023 Acre tax empty because the validated rate changed on April first` | APROVADO |
| CT-010 | Rótulo da alíquota | Tabela lida | Ver a tabela de alíquotas | Só o Acre aparece como Validado; as demais como pendentes; a tabela nunca aparece como homologada; falha de leitura cai nas pendentes e avisa | Passou | PG `marks the Acre modal rate as Validado and every other rate as pending legal validation`, `never presents the rate table as homologated, even for the validated Acre rate`, `falls back to pending rates and says so when the rate table cannot be read`; LG `labels the rate with its status`, `prefers a validated rate over a pending one and ignores revoked versions` | APROVADO |
| CT-011 | Transferências | Operação = Transferências | Escolher direção; trocar de operação; marcar ICMS | Direção só em Transferências e zera ao trocar; ICMS em transferência só por opção do usuário, como hipótese; direções nunca somadas; sem direção falha fechado | Passou | PG (describe `transfers`, 4 testes); LG (describe `transfer rules`, 2 testes) | APROVADO |
| CT-012 | Gráfico | Valor informado | Alterar o valor | Gráfico atualiza; no modo hipótese tem uma série por imposto e nenhuma série pública; entrada ausente fica vazia | Passou | PG `updates the chart as soon as the value changes`, `draws only the hypothesis, with no public series`; LG (describe `hypothesisChart`, 2 testes), `builds the chart with all public data and adds the simulated category`, `ignores an empty scenario in the chart` | APROVADO |
| CT-013 | Comparação com dados públicos bloqueada | Portão fechado | Tentar comparar | Comparação desabilitada, nenhum valor público preenchido | Passou | PG `keeps the comparison with public data disabled and never fills a public value` | APROVADO |
| CT-014 | Rótulo de hipótese | Qualquer resultado | Ler os textos com portão fechado e aberto | Resultado chamado de "estimado"; nunca "apurado" ou "devido" sem negação; aviso "não é imposto apurado nem devido" | Passou | PG describe `hypothesis labelling` (2 testes), `keeps the fields usable and labels every result as a manual hypothesis` | APROVADO |
| CT-015 | Tela estreita | Viewport de celular | Abrir com 360 px | Sem rolagem horizontal | Passou | PG `does not overflow horizontally on a narrow phone screen` | APROVADO |
| CT-016 | Rótulos por controle (acessibilidade automatizada) | Simulador aberto | Localizar cada controle pelo rótulo | Todo controle tem rótulo acessível | Passou (apenas a parte automatizada; ver CT-060) | PG `keeps every control reachable by label for keyboard and screen reader users` | APROVADO |
| CT-017 | Abertura pelo painel SPED | URL com UF e operação | Abrir `?uf=..&operacao=..` | Campos preenchidos; valores desconhecidos ignorados | Passou | PG describe `opened from the SPED panel` (2 testes) | APROVADO |
| CT-018 | Menu e rota | Aplicação carregada | Ver o menu e as rotas | Simulador acima de Visão geral e aberto por padrão; rotas protegidas conforme `app.routes.ts` | Passou | PG `sits above Visão geral in the menu and is open by default`; `apps/web/src/app/app.routes.spec.ts` (6 testes) | APROVADO |

## 2. Portão de confiabilidade

| ID | Caso | Pré-condição | Procedimento | Resultado esperado | Observado | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CT-020 | Portão fechado com o SPED NAO_CONFIAVEL (estado de hoje) | Nenhum indicador CONFERIDO | Abrir o Simulador | Dados públicos bloqueados com o motivo; nenhum número do SPED; lê só a linha de confiabilidade | Passou | PG `blocks the public data and says why, without rendering any SPED number`, `reads only the reliability row, never the full public data`, `uses the public-data free banner instead of the SPED banner` | APROVADO |
| CT-021 | Portão falha fechado | Resposta incompleta ou com erro | Bloco ausente; indicador ausente; um indicador não CONFERIDO; EXPLORATORIO; falha de leitura | Dados públicos bloqueados e campos mantidos | Passou | PG describe `fail closed` (5 testes) | APROVADO |
| CT-022 | Portão contra adulteração | Respostas forjadas | Entradas nulas, cópias duplicadas, CONFERIDO sem evidência, `publishableInSimulator` ausente | Fechado em todos os casos | Passou | GT describe `tampered or inconsistent answers (anti-circumvention)` (7 testes) | APROVADO |
| CT-023 | Portão aberto só com tudo CONFERIDO | Base futura simulada em teste | Todos CONFERIDO, publicáveis e com evidência | Abre, lê os dados completos e reabilita a comparação | Passou (simulação em teste; nenhum indicador real está CONFERIDO) | PG describe `once every indicator is CONFERIDO` (2 testes) | APROVADO |
| CT-024 | API: ID parecido ou nível forçado | API em teste | `fiscal-use` com IDs semelhantes e com nível enviado pelo chamador | Nunca autoriza | Passou | `tests/integration/test_reliability_bypass.py` (`test_lookalike_ids_never_authorize_fiscal_use`, `test_the_caller_cannot_force_the_level`) | APROVADO |
| CT-025 | API: todos os indicadores entregues | Registro real | `fiscal-use` para cada indicador | Todos recusados (409) | Passou | `test_every_shipped_indicator_is_refused_for_fiscal_use`, `test_the_block_never_marks_an_exploratorio_or_nao_confiavel_as_usable` | APROVADO |
| CT-026 | API: CONFERIDO completo e uso auditado | Registro de teste com responsável, data e evidência | `fiscal-use` | Só autoriza com evidência completa e audita o uso | Passou | `test_only_a_fully_evidenced_conferido_can_be_used_and_the_use_is_audited` | APROVADO |
| CT-027 | API: registro quebrado ou ausente | Registro inválido ou removido | Ler confiabilidade | Leituras falham em vez de abrir o portão | Passou | `test_a_broken_registry_makes_the_reads_fail_instead_of_opening_the_gate`, `test_a_missing_registry_also_fails_closed` | APROVADO |
| CT-028 | Regras do registro | Registros de teste | Carregar registros sem responsável, data, evidência; `conferred_at` no futuro | Carga recusada | Passou | `tests/unit/test_indicator_reliability.py` (23 testes) | APROVADO |
| CT-029 | Rotas de confiabilidade | API em teste | Ler bloco e `fiscal-use` | Contrato e estados corretos | Passou | `tests/integration/test_indicator_reliability_api.py` (4 testes) | APROVADO |

## 3. Segurança, acesso e auditoria

| ID | Caso | Procedimento | Resultado esperado | Observado | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| CT-030 | Sessão obrigatória | Chamar as 3 rotas sem token; com token malformado ou de outro emissor | 401 ou 403 | Passou | `tests/integration/test_simulador_access.py` (`test_every_route_requires_a_session`, `test_malformed_and_foreign_tokens_are_refused`) | APROVADO |
| CT-031 | Território e finalidade | Omitir cada cabeçalho | Recusado | Passou | `test_territory_and_purpose_are_required` | APROVADO |
| CT-032 | Isolamento entre tenants | Usar território ou finalidade de outro tenant | Recusado | Passou | `test_another_tenant_cannot_use_the_territory_or_purpose_of_this_one` | APROVADO |
| CT-033 | Administrador técnico sem login de operador | Ler conteúdo fiscal | Recusado | Passou | `test_technical_administrator_without_operator_login_cannot_read_fiscal_content` | APROVADO |
| CT-034 | Erros seguros | Provocar erro de validação e de conflito | Resposta `application/problem+json` segura, com `traceId`, sem pilha de execução | Passou | `test_validation_and_conflict_errors_are_safe_and_carry_a_trace_id` | APROVADO |
| CT-035 | Auditoria de leitura e de recusa | Ler alíquotas; ter o uso fiscal recusado | Evento de auditoria nos dois casos, mesmo quando a requisição falha | Passou | `test_reading_the_rate_table_is_audited`, `test_a_refused_fiscal_use_is_audited_even_though_the_request_fails` | APROVADO |
| CT-036 | Auditoria sem segredo | Inspecionar eventos | Sem segredo nem conteúdo da requisição | Passou | `test_audit_events_never_store_secrets_or_payloads` | APROVADO |
| CT-037 | Nenhuma publicação automática | Percorrer rotas e código | Nenhuma rota publica ou promove; nenhum código marca `published` ou CONFERIDO | Passou | `test_no_route_of_the_simulator_can_publish_or_promote_anything`, `test_no_code_promotes_an_indicator_or_publishes_the_sped_load` | APROVADO |
| CT-038 | Segregação de ambientes | Inspecionar o repositório | Só `.env.example` versionado, `.env` ignorado e nenhuma chave privada fora da fixture de teste | Passou | `test_environments_are_segregated_in_the_repository` | APROVADO |

## 4. Dados (SPED, CFOP, municípios)

| ID | Caso | Procedimento | Resultado esperado | Observado | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| CT-040 | Classificação de CFOP e direção | Classificar CFOPs com a tabela oficial da Sefaz-PE | Direção RECEBIDA ou REMETIDA; CFOP sem comprovação fica PENDENTE; somar direções é recusado | Passou | `tests/unit/test_cfop_transfers.py` (36 testes) | APROVADO |
| CT-041 | Ingestão e leitura do SPED em dados sintéticos | Executar a API, o leitor de planilha, a auditoria de omissões e a verificação de fonte | Contratos e contagens corretos | Passou | `tests/integration/test_sped_api.py` (11), `tests/unit/test_sped_xlsx.py` (13), `tests/unit/test_sped_omission_audit.py` (6), `tests/unit/test_sped_source_verify.py` (3) | APROVADO |
| CT-042 | Reconciliação com os originais | Rodar verify, reconcile e omission-audit | 46.825 células iguais ao original; 1.041 omissões (844 + 197); 16 verificações | 16 de 16 aprovadas | `evidence/ops/sped-homologacao-reconciliacao-20261028.md` | APROVADO |
| CT-043 | Catálogo de municípios do IBGE | Rodar `tools/ops/ibge-municipios-fetch.py --verify` e os testes | 5.571 municípios em 27 UFs com hash conferido | Passou | `tests/unit/test_ibge_municipios.py` (3); `evidence/ops/ibge-municipios-20261028.txt` | APROVADO |

## 5. Alíquotas e legislação

| ID | Caso | Procedimento | Resultado esperado | Observado | Evidência | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| CT-050 | Nenhuma alíquota homologada | Ler `GET /v1/tax-rates` | 31 versões; nenhuma homologada; cada item lista as lacunas | Passou | `tests/integration/test_tax_rates_api.py::test_no_seeded_rate_is_homologated_and_each_item_says_what_is_missing` | APROVADO |
| CT-051 | Acre 19% documentado e não homologado | Ler a linha do AC 19% | URL primária `legis.ac.gov.br/detalhar/5461`, exceções registradas, sem revisor, lacunas "revisão humana" e "homologação" | Passou | `test_acre_rows_carry_the_official_pages_and_validity_but_are_not_homologated`; `tests/unit/test_tax_rates_audit.py` | APROVADO |
| CT-052 | Parâmetros de simulação | Ler ITCD, ITBI e ISS | Nível SIMULACAO, sempre PENDENTE, nunca homologados, com limites de referência | Passou | `test_flat_taxes_are_simulation_parameters_with_reference_limits`; `tests/unit/test_tax_rates.py::test_a_simulation_parameter_is_never_homologated` | APROVADO |
| CT-053 | Restrições do cadastro | Gravar linhas inválidas | O banco recusa SIMULACAO validado, município sem código, janela de referência invertida, homologação sem validação, revisão pela metade e homologação sem revisão | Passou | `test_register_constraints_fail_closed` (8 casos), `test_register_rejects_the_same_municipality_operation_and_start_twice` | APROVADO |
| CT-054 | Resolução por jurisdição | Resolver alíquota com município | Alíquota de município vale só para ITBI e ISS e só para aquele município; nunca para a UF inteira | Passou | PG `uses a registered municipal ITBI rate only for that municipality, never for the whole UF`, `says that no municipal rate is registered...`, `never treats a municipality or operation rate as the rate of the whole UF`; `tests/unit/test_tax_rates.py` (17) | APROVADO |
| CT-055 | Auditoria das 31 versões | `python tools/ops/tax-rates-audit.py` | Relatório com lacunas por versão; 0 homologadas | 31 versões, 0 homologadas | `evidence/ops/aliquotas-homologacao-20261028.md` | APROVADO |
| CT-056 | Migração 0111 | `alembic upgrade head`, `downgrade -1`, `upgrade head` no banco sintético | Sem erro; head `0111_tax_rate_review_fields` | Sem erro | `evidence/ops/simulador-homologacao-20261028.txt` | APROVADO |

## 6. Não executados ou bloqueados

| ID | Caso | Motivo | Quem resolve | Estado |
| --- | --- | --- | --- | --- |
| CT-060 | Navegação por leitor de tela (NVDA, JAWS ou VoiceOver) e contraste medido | Exige pessoa e leitor de tela. O CT-016 cobre só os rótulos. | Responsável pela homologação funcional | NÃO EXECUTADO |
| CT-061 | Navegadores e dispositivos físicos | Os testes rodaram só em Chrome Headless 156 | Responsável pela homologação funcional | NÃO EXECUTADO |
| CT-062 | Homologação das alíquotas pelo revisor | Decisão humana (`reviewed_by`, `homologated_by`) | Revisor jurídico | NÃO EXECUTADO |
| CT-063 | Conferência do SPED e promoção a CONFERIDO | Decisão humana; falta definição de `Quantidade NF-e` | Responsável pela conferência dos dados | NÃO EXECUTADO |
| CT-064 | Valor total como preço unitário x quantidade | O requisito não define o cálculo. Hoje o valor informado é o total. | Responsável funcional | LACUNA |
| CT-065 | Carga das transferências recebidas (`.ods`) | Exige autorização para ingestão | Autoridade que autoriza | NÃO EXECUTADO |
| CT-066 | Aceite por usuários (UAT) | Exige usuários | Responsável pela homologação funcional | NÃO EXECUTADO |
| CT-067 | Teste de fumaça em produção | Sem deploy autorizado | Autoridade que autoriza | NÃO EXECUTADO |
| CT-068 | Alíquotas municipais de ITBI e ISS | Sem lei municipal nem fonte primária | Revisor jurídico | NÃO EXECUTADO |

## 7. Resumo da execução

| Medida | Valor |
| --- | --- |
| Casos planejados | 57 |
| Casos executados | 48 (84,2%) |
| Casos executados e aprovados | 48 (100% dos executados; 84,2% dos planejados) |
| Casos reprovados | 0 |
| Casos não executados ou com lacuna | 9 (CT-060 a CT-068) |

Contagens brutas da execução de 28/10/2026:

| Suíte | Resultado |
| --- | --- |
| pytest (completo) | 542 coletados: 533 passaram, 8 falharam, 1 ignorado |
| Karma (web) | 218 de 218 passaram |
| `ng build` | concluído sem erro |

As 8 falhas do pytest existiam antes desta fase e não têm relação com o Simulador. Estão em `tests/integration/test_alembic_paths.py` (4: `relation "gold_finance_state_summaries" already exists` ao subir do zero), `tests/integration/test_official_ingest.py` (1) e `tests/integration/test_source_ingest.py` (3). Ficam como dívida técnica e não entram na conta dos 57 casos.
