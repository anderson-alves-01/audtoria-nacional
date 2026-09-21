# Verdict 0.3.93

## Fatia

BCB OLINDA Expectativas trimestrais: nova fonte
`BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS` via `ExpectativasMercadoTrimestrais`
com allowlist IPCA + componentes Focus + Câmbio + PIB Total (`baseCalculo=1`).

## Evidencia tecnica

- Fixtures oficiais minimizadas (top=8 por indicador)
- Medianas: IPCA 1.5731; Livres 1.8052; Serviços 1.6767; Administrados 1.0629;
  Alimentação 3.3157; Bens industrializados 0.8018; Câmbio 5.1751; PIB Total 1.3
  (Data 2026-09-18)
- Layout `bcb-olinda-expectativas-trimestrais-v1`; silverCount 64
- Migration: `0096_bcb_olinda_trimestrais` -> implementation_version `0.3.93`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Selic/IGP/IPA/INPC trimestrais vazios na fonte; PIB setoriais congelados 2021 fora
- Sem carga nacional; sem credito
- Testes: 16 passed (sectoral) + unit trimestrais
- CI: apos push

## Proximo

Expandir trimestrais (PIB Serviços/Agro/Indústria 2021 opcional) ou UF tabular.
