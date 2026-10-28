# Relatório: Simulador SIRTA, confiabilidade e auditoria dos 1.041 pares

Data: 2026-10-28. Estado: tudo local, nada publicado. Produção segue com web 0.4.23 (`sirta-prod-web:31`) e API 0.3.124 (`sirta-prod-api:30`). Nenhum deploy, push ou ingestão foi feito.

## 1. Funcionalidades implementadas

### Preservação
- Os dois originais oficiais (`Estat_NFe_CFOP_por_UF_2016_a_2025_v1_formatada.ods`, `Estat_NFe_CFOP_2025_v1_formatada.ods`) agora estão versionados em `docs/data/originais/` (exceção explícita no `.gitignore`).
- `tools/ops/sped-source-verify.py` compara o sha256 e o tamanho dos originais com o manifesto `evidence/ops/sped-originais-20261028.txt`, e a planilha consolidada com o checksum da carga. Resultado atual: tudo confere.
- Os scripts `sped-source-fetch.py` e `sped-source-reconcile.py` e as evidências anteriores não foram alterados.

### Auditoria dos 1.041 pares
- `tools/ops/sped-omission-audit.py` atribui a cada par ausente a regra responsável e a classe (legítima, legítima material, indevida). Gera o relatório e um CSV com as 1.041 linhas indevidas.

### Controle de confiabilidade
- `config/indicator-reliability.yaml` registra NAO_CONFIAVEL, EXPLORATORIO ou CONFERIDO por indicador, com motivo e evidência. Nenhum indicador está CONFERIDO.
- `domain/indicator_reliability.py`: falha fechada (indicador ausente é NAO_CONFIAVEL). CONFERIDO exige quem conferiu, quando e evidência, ou o carregamento falha.
- API, só campos novos: bloco `reliability` em `GET /v1/sped-operacoes` e `GET /v1/tax-rates`, e `GET /v1/indicator-reliability/{id}/fiscal-use`, que devolve 409 para tudo que não é CONFERIDO. OpenAPI atualizado.

| Nível | Exibir | Hipótese rotulada | Cálculo fiscal | Publicar no Simulador |
|---|---|---|---|---|
| NAO_CONFIAVEL | só nas telas de referência, com aviso | não | não | não |
| EXPLORATORIO | com aviso | sim | não | não |
| CONFERIDO | sim | sim | sim | sim |

### Simulador (web, local)
- Portão dos dados públicos fechado: o Simulador lê só a linha de confiabilidade, descarta qualquer item que venha no corpo, não mostra mapa, tabela nem valores do SPED, e exibe um painel "Bloqueado" com o motivo de cada indicador e o que falta para liberar.
- Só existe a hipótese informada manualmente: quantidade e valor digitados, alíquota por UF e imposto, tudo rotulado "Hipótese informada manualmente". O gráfico mostra só a hipótese.
- A comparação com dados públicos está desabilitada, com aviso visível. O portão só abre quando todos os indicadores exigidos forem CONFERIDO e publicáveis (caminho coberto por teste, hoje inalcançável).
- Falha fechada: sem o bloco `reliability`, com indicador ausente, ou com erro de leitura, o portão fica fechado.
- A tela SPED de referência continua com o aviso "Fonte em revisão" e ganhou a lista de níveis por indicador.

### Tabela de alíquotas
- `tax_rate_versions` (migração `0109`, local) já estrutura UF, imposto, tipo, alíquota, vigência, fundamento legal, URL, responsável e status.
- Novo critério de homologação (`homologation_gaps`): VALIDADO mais fundamento legal, URL oficial, responsável e início de vigência conhecido. Cada item da API traz `homologated` e `homologationGaps`.
- Resultado: **0 de 31 versões homologadas**. O percentual lido de imagem não conta como fundamento legal. O AC está VALIDADO, mas sem URL oficial e, na faixa de 17%, sem início de vigência.
- `tools/ops/tax-rates-audit.py` gera `evidence/ops/aliquotas-homologacao-20261028.md`.

### Defeito corrigido no caminho
- `current-state.yaml` não era um YAML válido desde uma edição anterior (aspas duplas dentro do texto de `next_action`). Corrigido e coberto por teste.

## 2. Resultados da auditoria dos 1.041 registros

Fonte: `evidence/ops/sped-auditoria-omissoes-20261028.md` e `evidence/ops/sped-omissoes-1041-20261028.csv`.

A planilha publica a regra na aba "Fontes e método": Compras é 1/2/3.1xx e 1/2/3.401, .403, .406, .407; exclusões são códigos terminados em 00 ou 50 e entradas fora das sete categorias.

| Regra responsável | Classe | Células | NF-e |
|---|---|---:|---:|
| Agregador terminado em 00 ou 50 | legítima | 373 | 44.668.726 |
| Entrada fora dos grupos publicados | legítima, material | 20.929 | 16.693.931.316 |
| Nenhuma regra publicada | **indevida** | **1.041** | **268.317.945** |
| Total ausente (quantidade maior que zero, 2021 a 2025) | | 22.343 | 17.006.917.987 |

Invariante verificado: 21.302 legítimas + 1.041 indevidas = 22.343.

As 1.041 indevidas:
- Operação: todas "Compras" pela regra publicada.
- CFOPs: 1.151 a 1.154, 1.159, 1.190, 2.151 a 2.159, 2.170. Nenhum deles existe na `Base CFOP`, em nenhuma UF ou ano. A omissão atinge a `Base CFOP` e a `Série anual` ao mesmo tempo, por isso a conferência interna não a detecta.
- Maiores volumes por CFOP: 1.159 (81,0 milhões), 2.159 (55,1 milhões), 2.152 (43,2 milhões), 1.154 (25,8 milhões).
- Por ano (células, NF-e): 2021 (208, 48,4 milhões), 2022 (208, 51,4 milhões), 2023 (206, 52,1 milhões), 2024 (210, 61,4 milhões), 2025 (209, 55,0 milhões).
- Peso sobre as Compras incluídas: 10,9% no total. Por UF o omitido é 30,6 vezes as Compras incluídas em RO, 22,7 vezes no DF, 3,3 vezes em MS, 3,2 vezes no RN, 2,9 vezes no ES, 2,3 vezes no MA. SP, RS, PR e RJ ficam abaixo de 7%.
- Por operação: só Compras, nenhuma outra operação é afetada.

As legítimas seguem uma regra escrita na planilha, mas as entradas fora dos grupos somam 16,7 bilhões de NF-e e limitam a cobertura da base a 42,7% a 43,8% do histórico por ano.

Classificação: as 1.041 são omissões indevidas em relação à regra publicada. Se as transferências de entrada (1.15x e 2.15x) pertencem a Compras ou duplicam as saídas 5.15x e 6.15x é decisão metodológica pendente. Nenhum dado original foi alterado e nada foi reincluído.

## 3. Testes executados

| Verificação | Comando | Resultado |
|---|---|---|
| Suíte Python completa | `python -m pytest -q -p no:warnings` | 415 passaram, 1 ignorado, 8 falharam (pré-existentes, abaixo) |
| Testes novos Python | unitários de verificação, auditoria, confiabilidade, alíquotas e estado, e integração de confiabilidade e alíquotas | passaram |
| Contrato OpenAPI | `python -m pytest tests/contract` | 2 passaram |
| Web | `npx ng test --watch=false --browsers=ChromeHeadless` | 170 de 170 passaram |
| Build web | `npx ng build` | concluído sem erro |
| Lint | `ruff check` e `ruff format --check` nos arquivos novos e alterados | sem pendências |
| Originais | `python tools/ops/sped-source-verify.py` | 3 de 3 arquivos conferem |

Cobertura dos requisitos por teste:
- Falha fechada do portão: sem bloco, bloco incompleto, um indicador não conferido, EXPLORATORIO, erro de leitura.
- O Simulador não lê os dados completos e descarta itens recebidos com o portão fechado.
- A comparação fica desabilitada e nenhum valor público aparece.
- A API devolve 409 para NAO_CONFIAVEL, EXPLORATORIO e indicador desconhecido.
- Nenhuma alíquota é homologada, e a imagem não conta como fundamento legal.

As 8 falhas da suíte completa são anteriores a este trabalho e fora do escopo: 4 em `tests/integration/test_alembic_paths.py` (a cadeia de migrações falha na `0103` com tabela duplicada) e 4 em `test_source_ingest.py` e `test_official_ingest.py` (contagens do banco local, como 5571 contra 2). Não foram alteradas.

## 4. Bloqueios restantes

- A fonte SPED continua NAO_CONFIAVEL: as duas publicações do SPED não concordam por CFOP nem por entrada e saída, e nenhuma define "Quantidade NF-e". Não há correção possível do nosso lado.
- Compras por UF depende da decisão sobre 1.15x e 2.15x e de uma planilha reconciliada.
- Nenhuma alíquota está homologada. O ICMS do AC tem fundamento informado, sem URL oficial.
- Publicar o web remove a seção de dados públicos do Simulador em produção (hoje a versão 0.4.23 ainda mostra a Parte A com o aviso "Fonte em revisão").
- Publicar a API aplicaria a migração `0109` na inicialização.
- Tudo acima depende de autorização. Gates G0, G1, G4, G7, G8, G9 e G10 seguem NO-GO.

## 5. Informações necessárias para a homologação

1. Esclarecimento oficial do SPED sobre a definição de "Quantidade NF-e" e sobre a dimensão UF (emitente, destinatário ou outra).
2. Decisão do responsável sobre as entradas por transferência (CFOP 1.15x e 2.15x): Compras, categoria própria ou exclusão, com a regra escrita.
3. Nova versão da planilha, ou regra corrigida, reconciliada com os originais, incluindo a decisão sobre as entradas fora dos grupos que deixam a cobertura em 43%.
4. Revisão humana registrada em `config/indicator-reliability.yaml` (quem, quando, evidência) para promover qualquer indicador a CONFERIDO.
5. ICMS: URL oficial (legis.ac.gov.br) e início legal da alíquota de 17% do AC; para as outras 26 UFs, lei ou decreto da alíquota modal, início da vigência, URL oficial e responsável, uma UF por vez.
6. ITCD, ITBI e ISS: legislação aplicável por UF ou município. As alíquotas de 6%, 3% e 5% vieram do requisito do Simulador.
7. Autorização expressa para publicar API e web, sabendo dos efeitos descritos nos bloqueios.

## Rollback

Tudo está em commits locais separados. Para desfazer: `git revert` dos commits desta entrega, na ordem inversa. Nada em produção, banco ou nuvem foi alterado.
