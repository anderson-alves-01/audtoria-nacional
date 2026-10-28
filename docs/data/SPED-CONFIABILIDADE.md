# SPED NF-e por UF e CFOP: confiabilidade por indicador

Conferência feita em 2026-10-27 com os arquivos originais de gov.br/sped. Evidências:
`evidence/ops/sped-originais-*.txt` (URLs, tamanhos e sha256) e `evidence/ops/sped-reconciliacao-*.md`
(relatório completo). Script: `tools/ops/sped-source-reconcile.py`. Nenhum número foi corrigido.

## Resultado em uma linha

A nossa planilha consolidada repete o histórico original célula a célula (46.825 de 46.825). O problema
está na fonte ou na definição dela: o histórico por UF e a planilha mensal por CFOP somam o mesmo total
nacional em 2025 (8,33 bilhões de NF-e, diferença de 4.054), mas distribuem esse total de formas muito
diferentes entre CFOPs e entre entradas e saídas. Nenhum dos dois arquivos traz a definição de
"Quantidade NF-e". Falta esclarecimento do SPED.

## Níveis

- `NAO_CONFIAVEL`: não usar como referência fiscal nem para comparar UFs.
- `EXPLORATORIO`: pode aparecer com aviso, sem uso fiscal.
- `CONFERIDO`: reconciliado com a fonte original e com definição conhecida.

Nenhum indicador está em `CONFERIDO`.

## Matriz

| Indicador | Origem | Nível | Motivo | Evidência |
|---|---|---|---|---|
| Quantidade de NF-e por UF, CFOP e ano (2021 a 2025) | Histórico SPED por CFOP e UF, copiado sem alteração | NAO_CONFIAVEL | Valores incompatíveis com o porte da UF (SP com 1 a 2 NF-e no CFOP 5102; AC com 1,78 milhão em 2024 e 338 em 2025); saltos acima de 100x entre 2024 e 2025 em muitos pares UF e CFOP | Relatório, seções A, B, F |
| Compras por UF (planilha consolidada) | Planilha consolidada, operação Compras | NAO_CONFIAVEL | 1.041 pares UF x CFOP x ano (268,3 milhões de NF-e) classificados como Compras pela regra publicada estão ausentes | `sped-auditoria-omissoes-20261028.md` |
| Quantidade de NF-e por UF e ano, todos os CFOPs somados | Mesmo histórico | EXPLORATORIO | Soma por UF não bate com o porte esperado (SE acima de RJ e RS), mas o total das UFs bate com o total nacional | Relatório, seções C e D |
| Quantidade nacional de NF-e por CFOP e mês (2025) | Planilha mensal SPED | EXPLORATORIO | Definição ausente. Fecha com o histórico só no total geral, não por CFOP nem por entrada e saída | Relatório, seção C |
| Valor nacional por CFOP e mês (R$, 2025) | Planilha mensal SPED | EXPLORATORIO | Valor declarado pela fonte, sem conferência independente | Relatório, seção C |
| Valor estimado por UF, CFOP e ano (R$) | Rateio da planilha consolidada: valor nacional do CFOP x participação da UF na quantidade | NAO_CONFIAVEL | Herda o erro da quantidade por UF e CFOP, que define a participação. Não usar como referência fiscal | Relatório, seções A e C |
| Valor estimado por operação (UFs somadas) | Mesmo rateio, somado por operação | NAO_CONFIAVEL | Mesmo motivo; soma de valores rateados | Relatório, seção C |
| Imposto simulado no Simulador | Valor estimado x alíquota | NAO_CONFIAVEL | Deriva do valor estimado e de alíquotas ainda pendentes de validação jurídica (exceto AC modal) | `docs/data/DATA-PLATFORM.md` |

## Decisão sobre substituir ou corrigir a fonte

- Não há correção possível do nosso lado: a transformação não alterou números.
- A fonte substituta fica como pendência: pedir ao SPED a definição de "Quantidade NF-e" e da dimensão UF
  (emitente, destinatário ou outra), e a base UF x CFOP correta. Enquanto isso a carga atual permanece
  não homologada, não publicada e rotulada como exploratória.
- Itens sem regra de exclusão na planilha: 1.041 pares UF x CFOP x ano. Auditados em 2026-10-28, ver a
  seção "Auditoria dos 1.041 pares" abaixo.

## Auditoria dos 1.041 pares (2026-10-28)

Script `tools/ops/sped-omission-audit.py` (somente leitura). Evidências:
`evidence/ops/sped-auditoria-omissoes-20261028.md` e `evidence/ops/sped-omissoes-1041-20261028.csv`.
Nenhum dado original foi alterado e os dois originais oficiais estão versionados em
`docs/data/originais/` (verificação: `python tools/ops/sped-source-verify.py`).

| Regra | Classe | Células | NF-e |
|---|---|---:|---:|
| Agregador terminado em 00 ou 50 (aba "Fontes e método") | legítima | 373 | 44.668.726 |
| Entrada fora dos grupos publicados (aba "Fontes e método") | legítima, material | 20.929 | 16.693.931.316 |
| Nenhuma regra publicada | **indevida** | **1.041** | **268.317.945** |

- Todas as 1.041 são "Compras" pela regra publicada (1/2/3.1xx) e estão nos CFOPs 1.151 a 1.154, 1.159,
  1.190, 2.151 a 2.159 e 2.170. Esses CFOPs não existem na `Base CFOP` em nenhuma UF ou ano. A omissão
  atinge a `Base CFOP` e a `Série anual` juntas, por isso a conferência interna não a detecta.
- Peso: 10,9% das Compras incluídas na planilha (2,47 bilhões). Em RO o omitido é 30,6 vezes as Compras
  incluídas, no DF 22,7 vezes, em MS 3,3 vezes.
- As exclusões legítimas seguem uma regra escrita na planilha, mas as entradas fora dos grupos somam
  16,7 bilhões de NF-e e limitam o que a base representa (cobertura de 42,7% a 43,8% do histórico por ano).
- Decisão metodológica pendente: entradas por transferência (1.15x e 2.15x) podem duplicar as saídas
  por transferência (5.15x e 6.15x). Nada foi reincluído, corrigido ou promovido.

## Política de uso por nível (aplicada desde 2026-10-28)

Registro: `config/indicator-reliability.yaml`. Regras em `domain/indicator_reliability.py`.

| Nível | Exibir | Hipótese rotulada | Cálculo fiscal | Publicar no Simulador |
|---|---|---|---|---|
| NAO_CONFIAVEL | só nas telas de referência, com aviso | não | não | não |
| EXPLORATORIO | com aviso | sim | não | não |
| CONFERIDO | sim | sim | sim | sim |

- Indicador fora do registro é NAO_CONFIAVEL (falha fechada). CONFERIDO exige quem conferiu, quando e
  evidência, e o carregamento rejeita o arquivo sem esses campos. Nenhum script promove um nível.
- API: `GET /v1/sped-operacoes` e `GET /v1/tax-rates` trazem o bloco aditivo `reliability`.
  `GET /v1/indicator-reliability/{id}/fiscal-use` devolve 409 para tudo que não é CONFERIDO.
- Simulador: sem todos os indicadores públicos CONFERIDO, o portão fica fechado. Os dados públicos não
  são lidos nem exibidos, a comparação fica desabilitada e só existe a hipótese informada manualmente,
  rotulada "Hipótese informada manualmente". Ver `apps/web/src/app/shared/reliability/`.
- Alíquotas: percentual lido de uma imagem não é fundamento legal. Homologada exige VALIDADO mais fundamento
  legal, URL oficial, responsável e início de vigência. Hoje 0 de 31 versões atendem
  (`evidence/ops/aliquotas-homologacao-20261028.md`).

## O que não mudou

Produção continua com a carga `d25c890e-f93c-4b64-b307-247d64799e3f` (VALIDADA tecnicamente,
`published=false`, `homologated=false`, `createsTaxCredit=false`). Qualquer mudança em produção depende de
autorização.
