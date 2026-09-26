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
- Navegador local em `/executivo`, com a API publicada: abas, hexágono (Acre 888 mil), drawer, ranking com flash e busca "são" deixando só São Paulo.
- Larguras 1440, 1024 e 768 sem estouro da página. Em 375 a tabela rola dentro do próprio quadro.
- `/financeiro` abre com o título Dinheiro do Município. A carga desse painel seguiu lenta na API já publicada.

## Publicação

- Web `sirta-prod-web:0.4.9`, digest sha256:a4bf94d2093bdc9994d54f8d4109c6c2a60e2dc9441924a09f308331f2b784eb.
- Tarefa `sirta-prod-web:16`, rollout COMPLETED.
- `GET /executivo` 200. API permanece 0.3.114.
