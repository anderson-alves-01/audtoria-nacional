# Alíquotas: lacunas para a homologação (20261028)

Gerado por `tools/ops/tax-rates-audit.py`, somente leitura, a partir das linhas semeadas pela migração `0109_tax_rate_versions` e pelo ajuste da `0110_direction_rate_scope`. Nenhuma alíquota ou status foi alterado.

Critério de homologação: status `VALIDADO` e, ao mesmo tempo, fundamento legal, URL oficial da legislação, responsável pela validação, início da vigência conhecido e **homologação pelo responsável** (etapa humana separada: preencher a documentação não homologa). Percentual lido de uma imagem não atende a nenhum desses itens. Parâmetro de simulação (`SIMULACAO`) nunca é homologado como alíquota de UF ou município.

## Resumo

- Versões de alíquota: 31.
- Homologadas: **0**.
- Por status: PENDENTE 29, VALIDADO 2.

| Lacuna | Versões afetadas |
| --- | ---: |
| homologação pelo responsável | 31 |
| validação jurídica | 29 |
| fundamento legal | 29 |
| URL oficial da legislação | 29 |
| responsável pela validação | 29 |
| início da vigência | 29 |
| alíquota da jurisdição (parâmetro de simulação não é alíquota de UF ou município) | 3 |

## ICMS por UF

| UF | Alíquota (%) | Início | Fim | Status | Lacunas |
| --- | ---: | --- | --- | --- | --- |
| AC | 17 | 2002-01-01 | 2023-03-31 | VALIDADO | homologação pelo responsável |
| AC | 19 | 2023-04-01 | — | VALIDADO | homologação pelo responsável |
| AL | 20.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| AM | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| AP | 18 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| BA | 20.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| CE | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| DF | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| ES | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| GO | 19 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| MA | 23 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| MG | 18 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| MS | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| MT | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| PA | 19 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| PB | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| PE | 20.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| PI | 22.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| PR | 19.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| RJ | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| RN | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| RO | 19.5 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| RR | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| RS | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| SC | 17 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| SE | 19 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| SP | 18 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| TO | 20 | — | — | PENDENTE | validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |

## ITCD, ITBI e ISS

| Imposto | Competência | Nível | Alíquota (%) | Status | Lacunas |
| --- | --- | --- | ---: | --- | --- |
| ITCD | estadual | SIMULACAO | 6 | PENDENTE | alíquota da jurisdição (parâmetro de simulação não é alíquota de UF ou município); validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| ITBI | municipal | SIMULACAO | 3 | PENDENTE | alíquota da jurisdição (parâmetro de simulação não é alíquota de UF ou município); validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |
| ISS | municipal | SIMULACAO | 5 | PENDENTE | alíquota da jurisdição (parâmetro de simulação não é alíquota de UF ou município); validação jurídica; fundamento legal; URL oficial da legislação; responsável pela validação; início da vigência; homologação pelo responsável |

Os valores de 6%, 3% e 5% são parâmetros de simulação do requisito do Simulador. Não existe alíquota única nacional de ITCD, ITBI ou ISS: o cadastro relaciona imposto, localidade (UF ou município), operação, fundamento legal e vigência.

## O que falta informar

- AC: a documentação jurídica está completa (LC/AC 55/1997 art. 18, I, redação da LC/AC 422/2022, vigência 01/04/2023; redação anterior da LC/AC 100/2001, vigência 01/01/2002 a 31/03/2023, páginas da Sefaz/AC). Falta o responsável conferir os endereços e as condições de aplicação (exceções por mercadoria) e registrar a homologação.
- 26 UFs: lei ou decreto da alíquota modal, início da vigência, URL oficial, responsável pela validação e homologação, uma UF por vez.
- ITCD (estadual): lei de cada UF, alíquota, faixas, base e vigência. Limite de referência de 8% (Resolução do Senado nº 9/1992), informado e a conferir.
- ITBI (municipal): lei do município onde se situa o imóvel, alíquota, base e vigência.
- ISS (municipal): lei do município, item da lista de serviços, alíquota e vigência. Limites de referência de 2% a 5% (LC nº 116/2003), informados e a conferir.
- Exceções por mercadoria, operação interestadual e benefício fiscal não estão modeladas.
