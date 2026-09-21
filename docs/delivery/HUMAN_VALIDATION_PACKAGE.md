# Pacote de validação humana — Gold oficial (consolidação técnica)

Estado técnico: `DOC_HOMOLOGATION_PACKAGE_TECH_COMPLETE`  
`implementation_version`: ver `current-state.yaml`  
Branch de consolidação: `feat/official-public-ingest` / fatias sucessoras.  
Deploy AWS PROD: gate G10 separado — ver `docs/ops/G10-AUTHORIZATION.md`.

Este pacote **consolida** a evidência técnica para homologação humana. **Não** solicita aceite agora, **não** promove Gold e **não** autoriza produção.

Nenhum indicador abaixo está homologado, exigível, cobrável ou classificado como crédito tributário. Gold permanece `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`.

## O que a onda oficial PUBLIC_OPEN já processou tecnicamente

1. SIDRA 6579 (população) — quantidade de referência, não crédito.
2. SIDRA 5938 variável 37 (PIB) — quantidade de referência, não potencial de ISS.
3. SIDRA 5938 variável 6575 — quarentena quando a célula oficial é `...`, sem interpolação.
4. SIDRA 9509 CEMP (707/662/367) — ocupação, massa salarial e empresas; referência, não base de ISS.
5. SICONFI `/entes` — cadastro de cobertura, não demonstrativo fiscal.
6. Tesouro Aria `/custom/transferencias` — dicionário de tipos. FPM código 3 não é valor transferido.
7. Tesouro CKAN transferências mensais municipais (allowlist FPM/LC176/IOF-Ouro/COINT) — valores publicados com lineage.
8. SICONFI RREO, DCA e RGF — conectores particionados com checkpoint; carga limitada por `max_entes_per_run`.
9. EC 132 / LC 214 — documentos oficiais com retry; `binding=false`, `operational=false`, `homologated=false`.
10. Transferências estaduais ICMS/IPVA/IPI/CIDE e correlatas — UFs com fonte `PUBLIC_OPEN` tabular ativada; demais bloqueadas por formato/provenance.
11. Setoriais ANP/ANEEL/EPE/ANATEL/CNES e BCB SGS/OLINDA Expectativas (anuais, mensais, trimestrais, Selic reunião, Inflação 12/24m) — allowlist versionada.
12. RFB CNPJ — `READY_FOR_TERRITORIAL_SCOPE`, sem carga nacional.
13. Quinze dashboards oficiais — shell vazio quando não autorizado; sem crédito.
14. Domínios arrecadação, pagamentos, dívida ativa, procuradoria, cadastro 360, findings, casos, notificações — shells técnicos oficiais vazios / `CREDENTIAL_REQUIRED` onde couber.

## Divergência de cobertura

A diferença **5.571 versus 5.570** (IBGE 6579 versus SICONFI/entes e IBGE 5938) é cobertura pendente de homologação humana. Não é ocorrência administrativa.

## O que permanece institucionalmente aberto

- Gates humanos G0/G1/G4/G5/G7-oficial/G8-oficial/G9/G10 (`docs/delivery/HUMAN_DECISIONS_REQUIRED.md`).
- Aceite humano de Gold / dashboards / fórmulas.
- Fontes estaduais ainda sem tabular estável (RJ HTML IP-blocked, SP HTML-only, etc.).
- ISS/IPTU/ITBI/DA/pagamentos/processos municipais — `CREDENTIAL_REQUIRED`.
- `terraform apply` / deploy produção — exige ato G10 escrito.

## O que não validar como operação

Cobrança, constituição de crédito, diferença de transferência como ocorrência confirmada, regra IBS/CBS vinculante, ROI, potencial tributário como crédito, aceite institucional de dashboard, promoção de Gold.

## Evidências de consolidação

- `current-state.yaml`
- `docs/autonomous/ROADMAP-WORK-QUEUE.yaml` (item `DOC-HOMOLOGATION-PACKAGE`)
- `docs/delivery/HUMAN_DECISIONS_REQUIRED.md`
- Releases e ciclos em `docs/delivery/` e `docs/autonomous/`
