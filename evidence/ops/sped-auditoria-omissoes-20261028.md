# Auditoria das omissões da planilha SPED (20261028)

Gerado por `tools/ops/sped-omission-audit.py`, somente leitura. Compara o histórico oficial (UF x CFOP x ano, quantidade maior que zero, 2021 a 2025) com a base da planilha consolidada. Nenhum número original foi alterado. Os dois arquivos oficiais continuam em `docs/data/originais/`.

## 1. Regra responsável por cada célula ausente

| Regra | Classe | Células | Quantidade de NF-e | Justificativa |
| --- | --- | ---: | ---: | --- |
| AGREGADOR_00_50 | legitima | 373 | 44.668.726 | Exclusões da aba 'Fontes e método': códigos agregadores terminados em 00 ou 50. |
| ENTRADA_FORA_DOS_GRUPOS | legitima_material | 20.929 | 16.693.931.316 | Exclusões da aba 'Fontes e método': entradas que não cabem nas sete categorias. |
| SEM_REGRA_PUBLICADA | indevida | 1.041 | 268.317.945 | Nenhuma regra publicada. classify_cfop devolve uma operação, mas a célula não está na planilha. |
| **Total ausente** |  | **22.343** | **17.006.917.987** |  |

Invariante verificado: legítimas (21.302) + indevidas (1.041) = 22.343 células ausentes.

## 2. Cobertura por ano

| Ano | Histórico oficial (NF-e) | Incluído na planilha | Cobertura | Omissão indevida | Indevida / incluído |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2021 | 4.361.481.894 | 1.862.970.589 | 42,7% | 48.402.267 | 2,6% |
| 2022 | 4.879.711.335 | 2.101.989.785 | 43,1% | 51.371.457 | 2,4% |
| 2023 | 5.619.203.975 | 2.434.922.439 | 43,3% | 52.132.214 | 2,1% |
| 2024 | 6.808.624.948 | 2.946.662.430 | 43,3% | 61.398.115 | 2,1% |
| 2025 | 8.333.552.291 | 3.649.111.213 | 43,8% | 55.013.892 | 1,5% |

A cobertura baixa decorre das exclusões legítimas (entradas fora dos grupos). Ela limita o que a base representa, mas não é erro de transformação.

## 3. Omissões indevidas por operação

| Operação (regra publicada) | Células | Quantidade de NF-e |
| --- | ---: | ---: |
| Compras | 1.041 | 268.317.945 |

## 4. Omissões indevidas por ano

| Ano | Células | Quantidade de NF-e |
| ---: | ---: | ---: |
| 2021 | 208 | 48.402.267 |
| 2022 | 208 | 51.371.457 |
| 2023 | 206 | 52.132.214 |
| 2024 | 210 | 61.398.115 |
| 2025 | 209 | 55.013.892 |

## 5. Omissões indevidas por CFOP

| CFOP | Células | Quantidade de NF-e |
| --- | ---: | ---: |
| 1151 | 109 | 7.827.152 |
| 1152 | 121 | 9.797.136 |
| 1153 | 75 | 3.516.916 |
| 1154 | 112 | 25.839.590 |
| 1159 | 106 | 80.968.068 |
| 1190 | 4 | 4.223 |
| 2151 | 122 | 10.018.559 |
| 2152 | 124 | 43.239.168 |
| 2153 | 57 | 29.532.913 |
| 2154 | 124 | 2.465.662 |
| 2157 | 5 | 810 |
| 2158 | 5 | 2.349 |
| 2159 | 72 | 55.094.683 |
| 2170 | 5 | 10.716 |

## 6. Omissões indevidas por UF, com o peso sobre as Compras incluídas

`Indevida / Compras incluídas` mostra quantas vezes o volume omitido supera o que a planilha publica como Compras da UF no período.

| UF | Células | NF-e omitidas | Compras incluídas (NF-e) | Indevida / Compras incluídas |
| --- | ---: | ---: | ---: | ---: |
| MS | 45 | 60.376.385 | 18.339.750 | 3,29x |
| RO | 37 | 35.414.507 | 1.157.770 | 30,59x |
| RJ | 45 | 27.292.883 | 449.014.005 | 0,06x |
| PR | 49 | 27.155.240 | 576.819.899 | 0,05x |
| PB | 44 | 19.544.928 | 93.073.581 | 0,21x |
| MG | 50 | 14.443.133 | 137.495.329 | 0,11x |
| SC | 50 | 13.485.521 | 106.994.945 | 0,13x |
| PA | 45 | 12.354.479 | 109.028.011 | 0,11x |
| MA | 43 | 11.048.027 | 4.839.791 | 2,28x |
| RN | 35 | 8.799.247 | 2.773.539 | 3,17x |
| DF | 37 | 7.559.215 | 333.557 | 22,66x |
| SP | 50 | 6.098.925 | 419.217.560 | 0,01x |
| PE | 40 | 5.932.734 | 195.563.969 | 0,03x |
| MT | 40 | 4.651.161 | 168.549.924 | 0,03x |
| ES | 45 | 3.912.675 | 1.361.910 | 2,87x |
| AL | 39 | 3.274.114 | 4.253.098 | 0,77x |
| RS | 50 | 3.186.766 | 132.269.795 | 0,02x |
| GO | 62 | 1.829.403 | 1.813.660 | 1,01x |
| PI | 28 | 860.986 | 3.363.608 | 0,26x |
| CE | 31 | 645.204 | 3.258.204 | 0,20x |
| SE | 40 | 335.171 | 2.715.659 | 0,12x |
| TO | 27 | 49.021 | 8.744.088 | 0,01x |
| AP | 19 | 47.383 | 13.092.016 | 0,00x |
| AC | 23 | 13.864 | 240.468 | 0,06x |
| AM | 25 | 3.269 | 4.871.182 | 0,00x |
| BA | 32 | 2.699 | 1.185.377 | 0,00x |
| RR | 10 | 1.005 | 5.634.370 | 0,00x |

## 7. UF e ano mais afetados (omitido sobre Compras incluídas)

| UF | Ano | NF-e omitidas | Compras incluídas | Razão |
| --- | ---: | ---: | ---: | ---: |
| RO | 2021 | 7.335.676 | 197.727 | 37,10x |
| RO | 2022 | 7.847.884 | 215.332 | 36,45x |
| DF | 2024 | 1.765.539 | 58.509 | 30,18x |
| RO | 2023 | 7.134.529 | 236.844 | 30,12x |
| RO | 2025 | 6.616.288 | 245.825 | 26,91x |
| DF | 2025 | 1.915.650 | 71.960 | 26,62x |
| RO | 2024 | 6.480.130 | 262.042 | 24,73x |
| DF | 2023 | 1.334.623 | 56.464 | 23,64x |
| DF | 2022 | 1.324.216 | 76.188 | 17,38x |
| DF | 2021 | 1.219.187 | 70.436 | 17,31x |
| RN | 2021 | 1.908.956 | 358.441 | 5,33x |
| RN | 2022 | 1.870.916 | 370.262 | 5,05x |
| RN | 2023 | 1.937.141 | 409.126 | 4,73x |
| RN | 2024 | 1.843.630 | 415.462 | 4,44x |
| MS | 2022 | 10.750.357 | 2.873.145 | 3,74x |

## 8. Exclusões legítimas pela regra publicada, por CFOP (15 maiores)

| CFOP | Regra | Células | Quantidade de NF-e |
| --- | --- | ---: | ---: |
| 1923 | ENTRADA_FORA_DOS_GRUPOS | 115 | 2.187.246.104 |
| 1213 | ENTRADA_FORA_DOS_GRUPOS | 119 | 1.359.482.243 |
| 1921 | ENTRADA_FORA_DOS_GRUPOS | 120 | 736.642.004 |
| 1917 | ENTRADA_FORA_DOS_GRUPOS | 120 | 684.403.731 |
| 1454 | ENTRADA_FORA_DOS_GRUPOS | 72 | 512.863.563 |
| 1256 | ENTRADA_FORA_DOS_GRUPOS | 54 | 495.465.806 |
| 2208 | ENTRADA_FORA_DOS_GRUPOS | 117 | 489.078.344 |
| 1215 | ENTRADA_FORA_DOS_GRUPOS | 91 | 480.508.174 |
| 1664 | ENTRADA_FORA_DOS_GRUPOS | 121 | 478.316.961 |
| 1915 | ENTRADA_FORA_DOS_GRUPOS | 124 | 356.600.204 |
| 2453 | ENTRADA_FORA_DOS_GRUPOS | 67 | 353.121.834 |
| 1212 | ENTRADA_FORA_DOS_GRUPOS | 117 | 324.325.649 |
| 1922 | ENTRADA_FORA_DOS_GRUPOS | 117 | 309.377.819 |
| 2202 | ENTRADA_FORA_DOS_GRUPOS | 115 | 228.921.488 |
| 1933 | ENTRADA_FORA_DOS_GRUPOS | 114 | 224.378.076 |

## 9. Classificação

- **Legítimas.** Seguem uma regra escrita na planilha. Continuam sujeitas à revisão da definição de `Quantidade NF-e` pelo SPED, pois a regra de classificação é, nas palavras da própria planilha, aproximada.
- **Indevidas.** Pela regra publicada, os CFOPs 1.15x, 1.190, 2.15x e 2.170 pertencem a Compras, mas estão ausentes da `Base CFOP` e da `Série anual` em todas as UFs e anos. A omissão atinge as duas abas ao mesmo tempo, por isso a conferência interna da planilha não a detecta.
- **Decisão metodológica pendente.** Entradas por transferência (1.15x e 2.15x) podem duplicar as saídas por transferência (5.15x e 6.15x). O responsável deve decidir se pertencem a Compras, a uma categoria própria ou à exclusão. Enquanto isso, nada é reincluído nem corrigido.
- **Efeito.** A planilha não é homologável como está. O indicador de Compras por UF fica `NAO_CONFIAVEL` (ver `config/indicator-reliability.yaml`).

