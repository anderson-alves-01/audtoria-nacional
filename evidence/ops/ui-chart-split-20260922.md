# Correção das divergências de leitura — 2026-09-22

## O que mudou

- Gráficos deixam de somar naturezas diferentes e deixam de chamar série do IBGE de transferência.
- Cada variável publicada vira gráfico e indicador próprios, com a unidade do órgão.
- O eixo municipal usa o nome e o código IBGE, por exemplo São Paulo - SP (3550308).
- O cabeçalho mostra consulta pública, território e finalidade da sessão. O identificador fica só na dica do cursor.

## Evidência ao vivo

- API `sirta-prod-api:7`, imagem `0.3.103`, digest `sha256:04bdb6df9620adc09e3b00fb44c81712a5786cb877ccc2c6a01db9b35ca30859`.
- Web `sirta-prod-web:11`, imagem `0.4.4`, bundle `main-WAVMEGNI.js`, digest `sha256:7ee8b13ac5e62f9b5ace6f6c3513c6db665eaf5dad9a05e466dbd8d065470e22`.
- A frase do gráfico com um único ponto usa "1 ponto publicado".
- Executivo: `createsTaxCredit=false`, `commandsDisabled=true`, nenhum gráfico com unidade MIXED.
- CEMP separado: empresas 11.222.295 Unidades; salários 2.783.662.517 Mil Reais; pessoal ocupado 68.039.600 Pessoas.
- População: 214.211.951 Pessoas. PIB: 10.943.345.420 Mil Reais, variável "Produto Interno Bruto a preços correntes".
- Testes: `tests/unit/test_dashboard_charts.py` 3 passed. Specs Angular de painel e rótulos 4 passed.
- Integração `tests/integration/test_dashboards.py` não rodou: Postgres local em `localhost:55432` não respondeu.

## Rollback

- API: task definition `sirta-prod-api:5`, imagem `0.3.101`.
- Web imediato: task definition `sirta-prod-web:10`, imagem `0.4.3`.
- Web anterior: task definition `sirta-prod-web:9`, imagem `0.4.2`.

G10 permanece NO-GO.
