# Cycle — BCB OLINDA Expectativas trimestrais (0.3.93)

## Fatia

Nova fonte `BCB-OLINDA-EXPECTATIVAS-TRIMESTRAIS` via
`ExpectativasMercadoTrimestrais` com allowlist IPCA+componentes+Câmbio+PIB Total.

## Evidencia

- Fixtures oficiais minimizadas (top=8); medianas IPCA 1.5731 / Livres 1.8052 /
  Serviços 1.6767 / Administrados 1.0629 / Alimentação 3.3157 / Bens 0.8018 /
  Câmbio 5.1751 / PIB Total 1.3 (Data 2026-09-18)
- Layout `bcb-olinda-expectativas-trimestrais-v1`; silverCount 64
- Migration `0096_bcb_olinda_trimestrais` -> `0.3.93`
- Gold REFERENCE_QUANTITY; createsTaxCredit=false
- Selic/IGP/IPA/INPC vazios no entity set; PIB setoriais congelados 2021 fora

## Proximo

Expandir trimestrais (PIB Serviços/Agro/Indústria se aceitar série 2021) ou UF tabular.
