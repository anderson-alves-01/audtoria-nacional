# Alíquotas: lacunas para a homologação (20261028)

Gerado por `tools/ops/tax-rates-audit.py`, somente leitura, a partir das linhas semeadas pela migração `0109_tax_rate_versions`. Nenhuma alíquota ou status foi alterado.

Critério de homologação: status `VALIDADO` e, ao mesmo tempo, fundamento legal, URL oficial da legislação, responsável pela validação e início da vigência conhecido. Percentual lido de uma imagem não atende a nenhum desses itens.

## Resumo

- Versões de alíquota: 31.
- Homologadas: **0**.
- Por status: PENDENTE 29, VALIDADO 2.

| Lacuna | Versões afetadas |
| --- | ---: |
| URL oficial da legislação | 31 |
| início da vigência | 30 |
| validação jurídica | 29 |
| fundamento legal | 29 |
| responsável pela validação | 29 |

## ICMS por UF

| UF | Alíquota (%) | Início | Fim | Status | Lacunas |
| --- | ---: | --- | --- | --- | --- |
| AC | 19 | 2023-04-01 | — | VALIDADO | URL oficial da legislação |
| AC | 17 | — | 2023-03-31 | VALIDADO | URL oficial da legislação; início da vigência |
| AL | 20.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| AM | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| AP | 18 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| BA | 20.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| CE | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| DF | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| ES | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| GO | 19 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| MA | 23 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| MG | 18 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| MS | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| MT | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| PA | 19 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| PB | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| PE | 20.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| PI | 22.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| PR | 19.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| RJ | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| RN | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| RO | 19.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| RR | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| RS | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| SC | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| SE | 19 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| SP | 18 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| TO | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |

## ITCD, ITBI e ISS

| Imposto | Alíquota (%) | Status | Lacunas |
| --- | ---: | --- | --- |
| ITCD | 6 | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| ITBI | 3 | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |
| ISS | 5 | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência |

## O que falta informar

- AC: URL oficial (legis.ac.gov.br) das duas versões, início legal da alíquota de 17% e dispositivo exato.
- 26 UFs: lei ou decreto da alíquota modal, início da vigência, URL oficial e responsável pela validação, uma UF por vez.
- ITCD, ITBI e ISS: legislação aplicável por UF ou município. A alíquota única de 6%, 3% e 5% veio do requisito do Simulador.
- Exceções por mercadoria, operação interestadual e benefício fiscal não estão modeladas.
