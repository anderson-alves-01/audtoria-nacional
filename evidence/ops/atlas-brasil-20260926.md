# Atlas Brasil na visão executiva

Data: 2026-09-26. Sem alteração de API, modelo ou migration. `template/index.html` permanece intocado.

## O que entrou

- Tokens papel, tinta, verde, ocre e terracota, Fraunces, Archivo e textura de papel no shell.
- `/executivo` ganha o observatório: visão, mapa hex, ranking, comparador e metodologia.
- Os números saem de `GET /v1/dashboards/executivo/geography`.
- População em pessoas é mostrada em milhares. PIB permanece em mil reais.
- Nulo vira "—" e fica fora da escala de quantis.

## Conflitos mantidos

- A barra lateral de rotas continua. As abas do template são seções de `/executivo`.
- Os gráficos ECharts dos outros painéis continuam.
- A marca da aplicação continua SIRTA.

## TODO-dados

- Capital.
- PIB per capita.
- IDH, educação, saúde e infraestrutura.
- Série IDR do template (era derivada por hash, não foi portada).

## Verificação

- `ng test` do adaptador e do painel: 6 sucessos.
- A tela não foi percorrida no navegador nesta entrega.
