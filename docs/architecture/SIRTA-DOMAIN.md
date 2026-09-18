# Modelo de domínio SIRTA

## Agregados

### TaxCredit

Identidade, tenant, contribuinte, tributo, competência, origem, principal, acréscimos, moeda, validação, exigibilidade, cobrança, pagamento e versão.

### Validation

Checklist, evidências, parecer, responsável, autoridade aprovadora, data e decisão.

### CollectionCase

Caso, carteira, responsável, SLA, comunicações, providências, resposta, resultado e histórico.

### InstallmentAgreement

Adesão, parcelas, saldo, pagamentos, situação e rompimento.

### ActiveDebtEntry

Elegibilidade, controle de legalidade, inscrição, certidão, alterações, suspensão e baixa.

### TransferOccurrence

Modalidade, competência, fonte oficial, previsão, recebido, diferença, justificativa, evidências e conciliação.

### RegulatoryReadiness

Norma, obrigação, prazo, sistema afetado, responsável, teste, evidência e prontidão IBS/CBS.

## Invariantes

1. Todo registro pertence a um tenant e território.
2. Consulta sensível exige finalidade ativa.
3. Crédito não validado não entra em cobrança.
4. Suspensão ou impedimento bloqueia cobrança.
5. Pagamento só é recuperado após conciliação.
6. Mudança de estado gera evento de auditoria.
7. Evidência possui hash e origem.
8. Transferência não gera TaxCredit automaticamente.
9. Regra tributária é versionada e homologada.
10. Exclusões do ISR são justificadas e versionadas.

## Estados ortogonais

`validation_status`: IDENTIFIED, UNDER_REVIEW, VALIDATED, REJECTED, CANCELLED.  
`enforceability_status`: ENFORCEABLE, SUSPENDED, EXTINGUISHED, BLOCKED, LEGAL_REVIEW.  
`collection_status`: NOT_STARTED, ADMINISTRATIVE, ACTIVE_DEBT, LEGAL_COUNSEL, JUDICIAL, CLOSED.  
`payment_status`: OPEN, PARTIAL, PAID, COMPENSATED, INSTALLMENT_CURRENT, INSTALLMENT_BREACHED.

## Comando crítico

`StartAdministrativeCollection` deve verificar validação aprovada, exigibilidade, competência do usuário, finalidade, ausência de bloqueio e política vigente. A falha retorna problema tipado e não altera estado.

