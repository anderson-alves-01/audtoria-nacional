# Homologação dos dados do Simulador SIRTA

Data: 28/10/2026. Esta etapa reexecutou, somente em leitura, a verificação dos dados do SPED e registrou o estado de cada indicador. Nenhum dado foi carregado em banco, nenhum original foi alterado e nenhum indicador foi promovido.

## 1. Estado dos indicadores

Registro: `config/indicator-reliability.yaml`. Regra: só CONFERIDO pode alimentar cálculo fiscal ou ser publicado no Simulador. CONFERIDO exige responsável, data e evidência.

| Nível | Quantidade | Indicadores |
| --- | ---: | --- |
| CONFERIDO | 0 | Nenhum |
| EXPLORATORIO | 6 | `sped_quantidade_uf_ano`, `sped_quantidade_nacional_cfop_mes`, `sped_valor_nacional_cfop_mes`, `icms_aliquota_ac`, `icms_aliquota_demais_uf`, `itcd_itbi_iss_aliquotas` |
| NAO_CONFIAVEL | 6 | `sped_quantidade_uf_cfop_ano`, `sped_compras_uf`, `sped_valor_estimado_uf_cfop_ano`, `sped_valor_estimado_operacao`, `sped_transferencias_por_direcao`, `simulador_imposto_apurado_dados_publicos` |

Consequência: o portão do Simulador fica fechado. O Simulador funciona apenas com hipóteses informadas manualmente e a comparação com dados públicos está desabilitada.

## 2. Fontes e checksums

| Arquivo | sha256 | Resultado |
| --- | --- | --- |
| `docs/data/originais/Estat_NFe_CFOP_por_UF_2016_a_2025_v1_formatada.ods` | `195cabcaa4d242fda0794c817116f216119e958dafea3fd12e4224f9e191685a` | OK |
| `docs/data/originais/Estat_NFe_CFOP_2025_v1_formatada.ods` | `4dc50922f7e9f582fc08ded7a3e4442203a1f1be3a60f603e09fd8202dcf292e` | OK |
| `docs/data/Consolidado_Operacoes_UF_2021_2025_SPED.xlsx` | `1091967dd768b72152cc4c4a9b01b8637eebe45827c268f658ad462044e02cf3` | OK |
| `apps/web/public/ibge-municipios.json` (IBGE, 5.571 municípios) | `f34ffb9469ebb4f37a1ead3768aea7e25de700378819bbb002ccd042f6d0f5d0` | OK |

## 3. Reexecução da auditoria do SPED

Comandos: `python tools/ops/sped-source-verify.py`, `python tools/ops/sped-source-reconcile.py`, `python tools/ops/sped-omission-audit.py`, consolidados por `python tools/ops/sped-homologacao-evidence.py`. Os três saíram com código 0. Evidência: `evidence/ops/sped-homologacao-reconciliacao-20261028.md`.

| Verificação | Esperado | Observado |
| --- | --- | --- |
| Células UF x CFOP x ano da planilha | 46.825 | 46.825 |
| Células iguais ao original | 46.825 | 46.825 |
| Células diferentes ou sem correspondência | 0 | 0 |
| Células presentes no original e ausentes da planilha | 22.343 | 22.343 |
| Dessas, ausentes por regra publicada | 21.302 | 21.302 |
| Dessas, sem regra que explique (omissões) | 1.041 | 1.041 |
| Omissões recebidas e confirmadas / pendentes (células) | 844 / 197 | 844 / 197 |
| NF-e nas omissões (total, confirmadas, pendentes) | 268.317.945; 132.237.096; 136.080.849 | 268.317.945; 132.237.096; 136.080.849 |
| Originais alterados | nenhum | nenhum |
| Soma de direções recebida e remetida | recusada | recusada |

Resultado: 16 de 16 verificações aprovadas. A transformação não alterou números. O problema está na fonte ou na definição dela.

## 4. CFOP e direção das transferências

- Classificação pela tabela oficial da Sefaz-PE (`cfop.htm`, lida em 28/10/2026): só os CFOPs que a tabela lista como transferência são confirmados.
- Direção própria para recebidas (8 CFOPs) e remetidas (10 CFOPs). Direções nunca são somadas (`assert_single_direction`).
- Continuam PENDENTES, sem classificação comprovada: 1.159, 2.159, 1.190, 2.170, 1.155, 1.156, 1.157, 1.158, 5.154 e 5.157.
- Impacto da metodologia: das 380.140.367 NF-e que a planilha publica em Transferências, 38.882.859 (10,2%) estão em CFOPs que a tabela oficial não lista como transferência (`evidence/ops/sped-auditoria-omissoes-20261028.md`). O indicador fica ressalvado.
- A coluna `direcao` foi criada na migração 0110. As linhas de Transferências já existentes ficaram REMETIDA, porque todas eram de saída. Nenhuma linha foi apagada.

## 5. Municípios

- Lista oficial do IBGE (`https://servicodados.ibge.gov.br/api/v1/localidades/municipios`), obtida uma vez em 28/10/2026, sem credencial. É referência territorial, sem dado fiscal.
- 5.571 municípios em 27 UFs, com código de 7 dígitos, versionada em `apps/web/public/ibge-municipios.json`. Não há chamada externa em execução. Conferência: `python tools/ops/ibge-municipios-fetch.py --verify`.
- Evidência: `evidence/ops/ibge-municipios-20261028.txt`.

## 6. Limites que impedem o CONFERIDO

1. A definição de `Quantidade NF-e` não existe nas fontes. Os dois arquivos do SPED somam o mesmo total nacional em 2025 (diferença de 4.054), mas distribuem esse total de formas muito diferentes entre CFOPs e entre entradas e saídas.
2. Valores incompatíveis com o porte da UF (por exemplo, AC com 1,78 milhão de NF-e no CFOP 5102 em 2024 e 338 em 2025).
3. A planilha consolidada não traz as entradas por transferência. Os dados recebidos estão só nas planilhas `.ods` e a carga exige autorização.
4. Os valores por UF são rateios (valor nacional do CFOP x participação da UF na quantidade) e herdam o erro do item 2.

## 7. Estado da carga em produção

Inalterado. A execução `d25c890e-f93c-4b64-b307-247d64799e3f` permanece com `published=false`, `homologated=false` e `createsTaxCredit=false`. Nenhuma carga foi repetida.

## 8. Pendências para o CONFERIDO

| ID | Pendência | Responsável |
| --- | --- | --- |
| D-01 | Obter do SPED a definição de `Quantidade NF-e` e da dimensão UF (emitente, destinatário ou outra) | Responsável pela conferência dos dados |
| D-02 | Obter definição oficial dos CFOPs pendentes | Responsável pela conferência dos dados |
| D-03 | Autorizar a carga das transferências recebidas | Autoridade que autoriza |
| D-04 | Conferir os indicadores um a um e registrar responsável, data e evidência no registro | Responsável pela conferência dos dados |
| D-05 | Definir a regra para o valor por UF (rateio), ou substituir a fonte | Responsável pela conferência dos dados |

## 9. Decisão do responsável do projeto (28/10/2026, após a preparação)

- Definição adotada para Quantidade NF-e: **quantidade de itens**. É uma decisão do responsável do projeto, registrada em config/indicator-reliability.yaml. Ela não foi confirmada pelo SPED, porque as duas publicações não trazem definição. Os números da planilha não mudam.
- Efeito: o item D-01 passa a ter definição adotada, mas não confirmada na fonte.
- Não houve promoção a CONFERIDO. A definição não explica os volumes incompatíveis com o porte das UFs nem a divergência entre as duas publicações por CFOP e por entrada e saída (seção 6, itens 2 a 4), e a promoção exige responsável identificado, data e evidência no registro. Os 12 indicadores seguem como estavam.
- Consequência para a tela: rótulos que dizem "NF-e" passam a significar itens de NF-e. Esse ajuste de texto não foi feito nesta publicação e fica registrado como pendência de rotulagem.
