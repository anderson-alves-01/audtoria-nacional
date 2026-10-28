# Homologação jurídica das alíquotas do Simulador SIRTA

Data: 28/10/2026. Resultado: **nenhuma das 31 versões de alíquota está homologada.** Este documento registra o que foi documentado, o que foi lido nas fontes e o que falta. Homologar é um ato humano: `reviewed_by`, `reviewed_at` e `homologated_by` ficam vazios e nenhum código os preenche.

Critério usado (`homologation_gaps` em `apps/api/src/sirta_api/domain/tax_rates.py`): status VALIDADO e, ao mesmo tempo, fundamento legal, URL oficial, responsável pela validação, início da vigência conhecido, restrições e exceções registradas, revisão humana registrada (responsável e data) e homologação pelo responsável. Parâmetro de simulação nunca é homologado como alíquota de UF ou município.

## 1. Inventário das 31 versões

Auditoria: `python tools/ops/tax-rates-audit.py`. Relatório completo, versão por versão: `evidence/ops/aliquotas-homologacao-20261028.md`.

| Grupo | Versões | Status | Homologadas |
| --- | ---: | --- | ---: |
| ICMS do Acre | 2 | VALIDADO | 0 |
| ICMS das demais 26 UFs | 26 | PENDENTE (percentual lido de imagem do requisito) | 0 |
| ITCD, ITBI e ISS (6%, 3% e 5%) | 3 | PENDENTE, nível SIMULACAO | 0 |
| Total | 31 | VALIDADO 2, PENDENTE 29 | 0 |

Lacunas por quantidade de versões: revisão humana (31), homologação (31), restrições e exceções (30), validação jurídica, fundamento legal, URL oficial, responsável pela validação e início da vigência (29 cada) e "alíquota da jurisdição" (3, os parâmetros de simulação).

## 2. ICMS do Acre

### 2.1 Alíquota de 19% (desde 01/04/2023)

| Campo | Valor |
| --- | --- |
| Imposto, UF | ICMS, AC |
| Alíquota | 19% (modal, operações e prestações internas) |
| Vigência | 01/04/2023, sem data final |
| Fundamento | Lei Complementar Estadual nº 55/1997, art. 18, I, com a redação da LC/AC nº 422, de 26/12/2022 (publicada em 27/12/2022) |
| Fonte primária | https://www.legis.ac.gov.br/detalhar/5461 |
| Fontes complementares | https://sefaz.ac.gov.br/2021/?p=11479 e https://sefaz.ac.gov.br/2021/?p=12159 |
| Revisão humana | Vazia (`reviewed_by`, `reviewed_at`) |
| Homologação | Vazia (`homologated_by`) |
| Status | VALIDADO, não homologado |

A página da fonte primária foi lida em 28/10/2026 (leitura automatizada, somente leitura, sem envio de dado). Ela confirma o art. 1º da LC/AC 422/2022 e o art. 2º (vigência em 1º de abril de 2023). A leitura é conferência de fonte, não revisão humana.

### 2.2 Exceções registradas (campo `restrictions`)

Lidas no texto do art. 18 da LC 55/1997 como alterado pela LC/AC 422/2022:

| Inciso | Alíquota | Hipótese |
| --- | ---: | --- |
| I | 19% | Operações e prestações internas, ressalvadas as de alíquota específica |
| II, a | 12% | Operações e prestações interestaduais, ressalvado o disposto nos §§ 1º, 2º e 3º |
| II, b | 12% | Serviços de comunicação para empreendimentos de telemarketing e call center |
| III | 25% | Operações e prestações internas com joias, semijoias, bijuterias, perfumes e cosméticos (com exceções); cervejas sem álcool, refrigerantes e águas minerais (com exceção) |
| VII | 27% | Operações internas com cervejas e chopes, exceto cerveja sem álcool |
| VIII | 30% | Operações internas com fumos e seus derivados |
| IX | 33% | Operações internas com bebidas alcoólicas, exceto cervejas e chopes |
| X | 17% | Operações internas com produtos da cesta básica (itens definidos no regulamento do ICMS, § 4º) |

O art. 3º da LC/AC 422/2022 revoga os itens 2, 4, 7 e 8 do inciso III, as alíneas b e d do inciso V e o inciso VI.

### 2.3 O que não foi verificado

- O texto da página omite itens do inciso III e outros trechos (aparecem como reticências). A lista completa de exceções não foi transcrita.
- Os §§ 1º a 3º do art. 18 (que ressalvam a alíquota interestadual) não foram lidos.
- Alíquotas específicas previstas fora do texto lido.
- A lista de itens da cesta básica, que está no regulamento do ICMS.
- O Simulador usa só a alíquota modal interna. Exceção por mercadoria, operação interestadual e benefício fiscal não estão modelados.

### 2.4 Alíquota de 17% (01/01/2002 a 31/03/2023)

Fundamento informado: LC/AC 55/1997, art. 18, I, com a redação da LC/AC 100/2001, páginas da Sefaz/AC (`?p=12159`). A URL `legis.ac.gov.br/detalhar/5461` trata da LC 422/2022 e não comprova esse período. As exceções do período não foram levantadas e o campo `restrictions` fica vazio de propósito, para a lacuna continuar visível. Não homologada.

## 3. Demais 26 UFs

Percentuais lidos de uma imagem do requisito. Não há lei, decreto, URL oficial, início de vigência nem responsável. Nenhuma fonte primária foi consultada nesta fase e nenhum valor foi preenchido. No Simulador aparecem como "pendente de validação jurídica".

Para cada UF, o revisor precisa informar: lei ou decreto da alíquota modal, início da vigência, URL oficial, exceções, responsável pela validação, revisão e homologação.

## 4. ITCD, ITBI e ISS

| Imposto | Competência | Parâmetro | Referência informada (a conferir) |
| --- | --- | ---: | --- |
| ITCD | Estadual | 6% | Limite de 8%: Resolução do Senado nº 9/1992 |
| ITBI | Municipal | 3% | Sem limite informado |
| ISS | Municipal | 5% | Limites de 2% a 5%: LC nº 116/2003 |

- Os valores 6%, 3% e 5% vêm do requisito do Simulador. São hipóteses, não alíquotas de jurisdição, e o banco impede que sejam VALIDADO (`ck_tax_rate_simulation_not_validated`).
- Não existe alíquota única nacional desses impostos. O cadastro relaciona imposto, localidade (UF ou município), operação, fundamento e vigência.
- Nenhuma alíquota municipal está cadastrada. O seletor de município está implementado e a resolução pronta: uma linha de nível MUNICIPIO com código IBGE vale só para aquele município e só para ITBI e ISS. Sem linha, o Simulador informa que não há alíquota municipal e mantém o parâmetro de simulação.

## 5. Referências legais informadas e não conferidas

Registradas como informadas pelo responsável e ainda a conferir na fonte: LC 204/2023 (transferência entre estabelecimentos do mesmo titular, usada no aviso do Simulador), LC 227/2026, Resolução do Senado nº 9/1992 e LC 116/2003. Nenhuma delas foi lida nas fontes primárias nesta fase.

## 6. Garantias técnicas

- Migração 0111 (aditiva): colunas `restrictions`, `reviewed_by` e `reviewed_at`; CHECK exigindo revisor e data juntos (`ck_tax_rate_review_pair`) e revisão antes da homologação (`ck_tax_rate_homologated_reviewed`).
- Reversão: `alembic downgrade 0110_direction_rate_scope` (testada em upgrade, downgrade e upgrade).
- A API informa em cada item `homologated`, `homologationGaps`, `restrictions`, `reviewedBy` e `reviewedAt`. O web nunca mostra a tabela como homologada (CT-010).
- A leitura das alíquotas gera evento de auditoria (CT-035).

## 7. Pendências para a homologação definitiva

| ID | Pendência | Responsável |
| --- | --- | --- |
| J-01 | Conferir a lista completa de exceções do AC, os §§ 1º a 3º do art. 18 e a lista da cesta básica | Revisor jurídico |
| J-02 | Registrar revisão e homologação do ICMS AC 19% (e, se for o caso, do 17%) | Revisor jurídico |
| J-03 | Informar lei, vigência e URL de cada uma das 26 UFs, uma por vez | Revisor jurídico |
| J-04 | Informar a legislação de ITCD (por UF), ITBI e ISS (por município) | Revisor jurídico |
| J-05 | Conferir na fonte as referências LC 204/2023, LC 227/2026, Res. SF 9/1992 e LC 116/2003 | Revisor jurídico |
| J-06 | Definir como tratar exceção por mercadoria e operação interestadual no Simulador | Responsável funcional |
