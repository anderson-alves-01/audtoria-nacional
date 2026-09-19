# Operação de ingestão PUBLIC_OPEN (local)

## Regras

- Somente fontes `PUBLIC_OPEN` em runtime.
- Snapshots oficiais minimizados apenas em testes.
- Sem sintético em Landing/Bronze/Silver/Gold/API/dashboard.
- Toda linha Gold exige lineage até Silver, Bronze, manifesto, checksum SHA-256 e URL.
- Fonte pública nunca cria crédito, cobrança, inscrição ou notificação.

## Execução controlada

1. Confirmar `source_id` em `contracts/sources/official-catalog.yaml`.
2. Definir competência e `max_entes_per_run` / escopo territorial.
3. Executar job com `run_id`; registrar manifesto e contagens.
4. Em falha de schema/licença/domínio: suspender conector.

## Proibições

- Carga nacional ilimitada sem autorização.
- RFB sem `territorial_scope`.
- Portal da Transparência sem credencial.
- `terraform apply` e deploy.
