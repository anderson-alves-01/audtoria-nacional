# Pacote de validação humana — Gold oficial 0.3.15

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

Este pacote **não** encerra o ROADMAP. A declaração `REAL_DATA_PIPELINES_COMPLETE_AWAITING_HUMAN_VALIDATION` foi prematura e não deve ser usada enquanto existirem fontes públicas ativáveis, dashboards, domínios ou itens técnicos em aberto.

Nenhum indicador abaixo está homologado, exigível, cobrável ou classificado como crédito tributário. Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.

## O que a onda 1 já processou tecnicamente

1. SIDRA 6579 (população) — quantidade de referência, não crédito.
2. SIDRA 5938 variável 37 (PIB) — quantidade de referência, não potencial de ISS.
3. SIDRA 5938 variável 6575 — permanece em quarentena quando a célula oficial é `...`, sem interpolação.
4. SICONFI `/entes` — cadastro de cobertura, não demonstrativo fiscal.
5. Tesouro Aria `/custom/transferencias` — dicionário de tipos. FPM código 3 não é valor transferido.
6. Tesouro CKAN `Transferencia_Mensal_Municipios_202609.csv` — valores de FPM publicados (join IBGE via SICONFI/entes).
7. SICONFI RREO e DCA — conectores particionados com checkpoint; carga nacional limitada por `max_entes_per_run`.
8. EC 132 — documento oficial com retry/Senado; `binding=false`, `operational=false`, `homologated=false`.

## Divergência de cobertura

A diferença **5.571 versus 5.570** (IBGE 6579 versus SICONFI/entes e IBGE 5938) é cobertura pendente de homologação. Não é ocorrência administrativa.

## O que permanece em aberto (não solicitar validação humana agora)

- Backfill nacional controlado de RREO/DCA/FINBRA.
- Ativação estadual ICMS/IPVA somente após fonte PUBLIC_OPEN estruturada verificada.
- RFB CNPJ — `READY_FOR_TERRITORIAL_SCOPE`, sem carga nacional.
- ISS/IPTU/ITBI/DA/pagamentos/processos — `CREDENTIAL_REQUIRED`.
- Demais itens técnicos do ROADMAP 1.2 e operação de piloto/produção.

## O que não validar como operação

Cobrança, constituição de crédito, diferença de transferência como ocorrência confirmada, regra IBS/CBS vinculante, ROI, potencial tributário como crédito, aceite institucional de dashboard.
