# Release notes 0.3.71

## Entrega

- BCB OLINDA Expectativas Focus anuais: `Dívida líquida do setor público`
  (`PERCENT_OF_GDP`, baseCalculo=0) e `Balança comercial` Saldo
  (`USD_BILLION`, filtro `IndicadorDetalhe`).
- Conector `bcb_olinda_expectativas` passa a aceitar `indicator_detalhe`.
- Layout `bcb-olinda-expectativas-anuais-v6`; silverCount esperado 96 (12×8).
- Migration Alembic `0074_bcb_olinda_divida_balanca` → `0.3.71`.
- Re-probe UF restantes: nenhum `ACTIVATE_NOW`.

## Não entregue

- Homologação humana do Gold.
- Ativação de UFs PDF/HTML/IP-blocked.
- Exportações/Importações da Balança comercial.
