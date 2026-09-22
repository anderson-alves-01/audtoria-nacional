# Release notes 0.3.15

Estado: `OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS`

A declaração `REAL_DATA_PIPELINES_COMPLETE_AWAITING_HUMAN_VALIDATION` foi retirada. A onda 1 de fontes públicas oficiais permanece tecnicamente processada, com Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`, e o ROADMAP 1.2 continua em progresso.

## Nesta fatia

- Lineage Gold por linha (Silver, Bronze SHA-256, manifesto Landing, URL oficial).
- Tesouro CKAN `Transferencia_Mensal_Municipios_202609.csv` como fonte estruturada de FPM municipal.
- SICONFI RREO e DCA com particionamento, checkpoint e `max_entes_per_run`.
- EC 132 com retry e endpoint alternativo do Legis Senado; documento `NON_BINDING`.
- Catálogo estadual ICMS/IPVA dos 26 estados e DF, sem ativação não verificada.
- RFB CNPJ em `READY_FOR_TERRITORIAL_SCOPE`, sem carga nacional.
- Conectores municipais restritos vazios `CREDENTIAL_REQUIRED`.
- Quinze dashboards oficiais; módulos sem fonte permanecem vazios.
- Invariantes automáticas: lineage completo, sem fixture de teste no runtime, metadados ≠ valor financeiro, fonte pública ≠ crédito, quarentena ≠ Gold.

## Não concluído

Backfill nacional ilimitado, fontes estaduais estruturadas, território RFB, dados municipais reais, piloto, produção e homologação humana.
