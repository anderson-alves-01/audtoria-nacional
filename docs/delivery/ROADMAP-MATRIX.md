# Matriz técnica ROADMAP 1.2 versus código (pós-0.3.12)

Gerada em 2026-09-18. Spec `0.3.0`. Branch `feat/roadmap-technical-completion`.

| Requisito | Dependências | Estado | Evidência | Testes | Gate | Bloqueio | Próxima ação |
|---|---|---|---|---|---|---|---|
| Higiene Alembic | nenhuma | feito 0.3.8 | `evidence/releases/0.3.8/` | `test_alembic_paths` | LOCAL_GO | — | — |
| F0 identidade/isolamento | — | feito 0.3.1 | `evidence/releases/0.3.1/` | isolation | LOCAL_GO | — | — |
| Validação/cobrança/funil/G6-G8 local | F0 | feito 0.3.2-0.3.7 | releases 0.3.2-0.3.7 | suíte atual | LOCAL_GO / G7-G8 OFFICIAL_BLOCKED | homologação | manter flags |
| F3.0 Registro Mestre de Fontes | 0.3.8 | feito 0.3.9 | `evidence/releases/0.3.9/` | `test_catalog` | G3 técnico local; G0/G1 oficial BLOCKED | ingestão real | — |
| F3.1 ingestão sintética genérica | F3.0 | feito 0.3.11 IBGE + 0.3.12 Tesouro stub | `evidence/releases/0.3.12/` | `test_source_ingest` | LOCAL_GO | dado real / conector oficial | — |
| F3.2 conectores públicos oficiais | F3.0, G0/G1 | catálogo + stubs sintéticos | 0.3.12 | mock contratual | OFFICIAL_BLOCKED | credencial/volume | dry-run oficial após G0 |
| F3.3 fontes municipais restritas | G0/G1 | bloqueado | — | estado DISCOVERED | BLOCKED | DPA | interface sem ingestão |
| G0/G1 checklists | — | UI/API BLOCKED 0.3.12 | `evidence/releases/0.3.12/` | `test_gates` | BLOCKED | decisão humana | aguardar autorização |
| G4 regras ISS reais | G1 | genérico local | — | não inventar fórmula | BLOCKED | especialista | feature flag off |
| G7 conectores Tesouro | F3.0 | ocorrência local + stub sintético | 0.3.12 | nunca cria crédito | LOCAL_GO/OFFICIAL_BLOCKED | credencial | sem conector oficial |
| G8 calendário oficial | G8 local | NON_BINDING | 0.3.7 | binding false | LOCAL_GO/OFFICIAL_BLOCKED | homologação | manter |
| Terraform generate/validate | F0 | docs locais 0.3.10 | `evidence/releases/0.3.10/` | fmt/validate | G10 BLOCKED | apply | módulos sem apply |
| G9/G10 | G0 | bloqueado | — | — | BLOCKED | aceite | checklists |

DAG: `0.3.12 Tesouro stub + G0/G1 UI → terraform modules no-apply`. Parar em G0/G1/G4/G7 oficial/G8 oficial/G9/G10.
