---
name: transfer-reconciliation
description: Build or review monitoring and reconciliation of constitutional and legal transfers to municipalities.
---
# Transfer Reconciliation

Treat FPM, ICMS/IPVA shares, ITR, IPI-Exportação, CIDE, FUNDEB, royalties and configured transfers as a separate bounded context.

For each record retain official source, competence, coefficient/base when available, expected value, received value, adjustments, retention/block status and reconciliation evidence.

A difference creates `TransferOccurrence`, never `TaxCredit`. Automatic conclusions, collection and legal claims are prohibited. Data-contract-first tests must cover missing competence, duplicate source records, revisions, partial receipts and reconciliation.

