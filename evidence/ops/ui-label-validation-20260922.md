# Validação da leitura dos painéis — 2026-09-22

Veredito: alinhado à regra de referência sem crédito, com divergência na medida dos gráficos.

## Evidência

- Tela ao vivo: `GET /executivo` no ALB, bundle `main-H2FVPIQV.js`, task `sirta-prod-web:9`.
- API: `GET /v1/dashboards/executivo|economia|financeiro|transferencias` com sessão PUBLIC_OPEN.
- Flags do executivo: `createsTaxCredit=false`, `commandsDisabled=true`, `taxPotentialAsCredit=false`, `roiCalculated=false`.
- Spec permanece `0.3.0`. Pacote web `0.4.0`. API `0.3.101` não foi republicada.
- Testes locais desta fatia: 9 specs Angular (labels, dashboard, funil, fontes, setorial) com exit 0.

## O que a tela do executivo mostra

- População estimada publicada pelo IBGE: 214.211.951, competência 2026, 5.571 registros.
- Cadastro Central de Empresas: 2.862.924.412, competência 2024, 16.710 registros.
- PIB municipal publicado pelo IBGE: 10.943.345.420, competência 2023, 5.570 registros.
- Cadastro SICONFI e divergência de cobertura sem valor publicado.
- Texto de validação: consulta de referência, sem crédito e sem cobrança.
- Códigos `REFERENCE_QUANTITY`, `ibge_gdp_and_services_va` e `REAL_OFFICIAL_DATA_*` não aparecem na leitura.

## Divergências

1. O gráfico "Top 10 municípios" declara medida "Valor de transferência publicado pelo órgão" porque a API fixa `valueKind=TRANSFER_AMOUNT_AS_PUBLISHED`. No executivo os pontos são códigos IBGE (3550308, 3304557, 5300108), não repasse do Tesouro.
2. "Total publicado por competência" coloca população, CEMP e PIB no mesmo eixo. Há aviso de que não formam total único. A definição pede que naturezas diferentes não sejam apresentadas como equivalentes.
3. O total do CEMP é uma soma única de ocupação, massa salarial e empresas. A frase da fonte explica as três medidas; o número não as separa.
4. O cabeçalho ainda mostra `PUBLIC_OPEN_UI_BOOTSTRAP` e os identificadores de território e finalidade.
5. `current-state.yaml` ainda diz para não fazer deploy. A imagem 0.4.2 está no ar e a alteração não está commitada. G10 permanece NO-GO. Lighthouse e E2E desta imagem não foram reexecutados.

## Alinhado

- PIB permanece quantidade de referência, como no pacote de validação humana de 2026-09-21, e a frase diz que não é potencial de ISS.
- Comandos de cobrança seguem desativados.
- Lineage fica atrás de "Exibir lineage".
- Contratos da API não foram alterados.
