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
- Itens sem regra de exclusão na planilha: 1.041 pares UF x CFOP x ano do original com quantidade maior
  que zero estão fora da planilha sem que a regra publicada de exclusão os explique. Registrar e revisar
  junto com o esclarecimento.

## O que não mudou

Produção continua com a carga `d25c890e-f93c-4b64-b307-247d64799e3f` (VALIDADA tecnicamente,
`published=false`, `homologated=false`, `createsTaxCredit=false`). Qualquer mudança em produção depende de
autorização.
