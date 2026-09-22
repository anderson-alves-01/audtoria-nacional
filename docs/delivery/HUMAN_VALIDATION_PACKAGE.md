# Pacote de validação humana — Gold oficial (referência PUBLIC_OPEN)

Estado: `REFERENCE_ONLY_HUMAN_VALIDATED`  
`implementation_version`: ver `current-state.yaml`  
Status Gold pós-ato: `REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY`  
`createsTaxCredit`: **false** · `commandsDisabled`: **true**

## Ato humano registrado

| Campo | Valor |
| --- | --- |
| Data | 2026-09-21 |
| Responsável | Operador do tenant (validação nesta conversa de entrega) |
| Escopo | **A — REFERENCE_ONLY** indicadores `PUBLIC_OPEN` de referência já no Gold |
| Decisão | Homologar **somente** como referência citável para painéis; **não** crédito |
| Proibições | Sem cobrança, ISS, dívida, potencial como crédito, G0/G1/G4/G9 |

Este ato **não** libera gates institucionais G0/G1/G4/G9 nem constitui crédito tributário.  
IA não decide, acusa, autua ou publica — recomenda e cita evidências Gold.

## Escopo A homologado (referência)

1. SIDRA 6579 (população) — quantidade de referência, não crédito.
2. SIDRA 5938 variável 37 (PIB) — quantidade de referência, não potencial de ISS.
3. SIDRA 5938 variável 6575 — quarentena quando a célula oficial é `...`, sem interpolação.
4. SIDRA 9509 CEMP (707/662/367) — ocupação, massa salarial e empresas; referência, não base de ISS.
5. SICONFI `/entes` — cadastro de cobertura, não demonstrativo fiscal.
6. Tesouro Aria `/custom/transferencias` — dicionário de tipos. FPM código 3 não é valor transferido.
7. Tesouro CKAN transferências mensais municipais (allowlist FPM/LC176/IOF-Ouro/COINT) — valores publicados com lineage.
8. SICONFI RREO, DCA e RGF — conectores particionados; carga limitada por `max_entes_per_run`.
9. EC 132 / LC 214 — documentos oficiais; `binding=false`, `operational=false` (contagem/docs, não regra vinculante).
10. Transferências estaduais ICMS/IPVA/IPI/CIDE — UFs com fonte `PUBLIC_OPEN` tabular ativada.
11. Setoriais ANP/ANEEL/EPE/ANATEL/CNES e BCB SGS/OLINDA — allowlist versionada.
12. Quinze dashboards oficiais — gráficos/KPIs apenas a partir de Gold; shells vazios premium quando sem Gold.

## Fora do escopo (permanece bloqueado)

- Cobrança, constituição de crédito, inscrição em dívida, parcelamento operacional.
- ISS/IPTU/ITBI/DA/pagamentos/processos municipais — `CREDENTIAL_REQUIRED`.
- Diferença de transferência como ocorrência administrativa confirmada.
- Regra IBS/CBS vinculante; ROI; potencial tributário como crédito.
- Gates G0/G1/G4/G5/G7-oficial/G8-oficial/G9 (G10 infra é ato separado).

## Divergência de cobertura

A diferença **5.571 versus 5.570** (IBGE 6579 versus SICONFI/entes e IBGE 5938) permanece anotada como cobertura — **não** ocorrência administrativa.

## Evidências

- `current-state.yaml`
- `docs/delivery/RELEASE_NOTES_0.3.99.md`
- `evidence/releases/0.3.99/`
- API `GET /v1/dashboards/{id}` com `kpis` / `charts` e `evidenceIds`
