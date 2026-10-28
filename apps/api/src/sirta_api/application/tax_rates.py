"""Read access to the versioned tax rates."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import TaxRateVersion
from sirta_api.application.audit import record_audit
from sirta_api.application.indicator_reliability import RATE_INDICATORS, reliability_for
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ValidationFailedError
from sirta_api.domain.tax_rates import RateVersion, homologation_gaps, resolve_on

TAXES = ("ICMS", "ITCD", "ITBI", "ISS")
UFS = (
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "BR",
)  # fmt: skip
NOTICE = (
    "Alíquotas para simulação. Só as marcadas VALIDADO têm base legal registrada. PENDENTE não é "
    "validação jurídica. Alíquota modal: exceções por mercadoria e operação não estão modeladas. "
    "ITCD (estadual), ITBI e ISS (municipais) aparecem como parâmetros de simulação, não como "
    "alíquota de UF ou município; nenhuma linha está homologada sem o revisor responsável."
)


def _item(row: TaxRateVersion) -> dict:
    gaps = homologation_gaps(
        status=row.status,
        legal_basis=row.legal_basis,
        official_url=row.official_url,
        validated_by=row.validated_by,
        valid_from=row.valid_from,
        homologated_by=row.homologated_by,
        jurisdiction_level=row.jurisdiction_level,
    )
    return {
        "homologated": not gaps,
        "homologationGaps": gaps,
        "tax": row.tax,
        "uf": row.uf,
        "jurisdictionLevel": row.jurisdiction_level,
        "isSimulationParameter": row.jurisdiction_level == "SIMULACAO",
        "municipalityIbgeCode": row.municipality_ibge_code,
        "operationRef": row.operation_ref,
        "referenceMin": float(row.reference_min) if row.reference_min is not None else None,
        "referenceMax": float(row.reference_max) if row.reference_max is not None else None,
        "homologatedBy": row.homologated_by,
        "homologatedAt": row.homologated_at.isoformat() if row.homologated_at else None,
        "rateKind": row.rate_kind,
        "rate": float(row.rate),
        "validFrom": row.valid_from.isoformat() if row.valid_from else None,
        "validTo": row.valid_to.isoformat() if row.valid_to else None,
        "legalBasis": row.legal_basis,
        "officialUrl": row.official_url,
        "status": row.status,
        "validatedBy": row.validated_by,
        "validatedAt": row.validated_at.isoformat() if row.validated_at else None,
        "note": row.note,
    }


def list_tax_rates(
    session: Session,
    *,
    context: AccessContext,
    tax: str | None = None,
    uf: str | None = None,
    on: str | None = None,
) -> dict:
    context.ensure_fiscal_read()
    if tax is not None and tax not in TAXES:
        raise ValidationFailedError(f"Imposto inválido: {tax!r}.")
    if uf is not None and uf not in UFS:
        raise ValidationFailedError(f"UF inválida: {uf!r}.")
    on_date: date | None = None
    if on is not None:
        try:
            on_date = date.fromisoformat(on)
        except ValueError as error:
            raise ValidationFailedError("Data inválida; use AAAA-MM-DD.") from error
    query = select(TaxRateVersion).where(TaxRateVersion.status != "REVOGADO")
    if tax is not None:
        query = query.where(TaxRateVersion.tax == tax)
    if uf is not None:
        query = query.where(TaxRateVersion.uf == uf)
    rows = list(
        session.scalars(
            query.order_by(TaxRateVersion.tax, TaxRateVersion.uf, TaxRateVersion.valid_from)
        )
    )
    body: dict = {
        "notice": NOTICE,
        "createsTaxCredit": False,
        "reliability": reliability_for(RATE_INDICATORS),
        "on": on,
        "resolved": None,
    }
    if on_date is not None and tax is not None and (uf is not None or tax != "ICMS"):
        versions = [
            RateVersion(
                tax=row.tax,
                uf=row.uf,
                rate_kind=row.rate_kind,
                rate=row.rate,
                valid_from=row.valid_from,
                valid_to=row.valid_to,
                status=row.status,
                jurisdiction_level=row.jurisdiction_level,
                municipality_ibge_code=row.municipality_ibge_code,
                operation_ref=row.operation_ref,
                homologated_by=row.homologated_by,
            )
            for row in rows
        ]
        resolved = resolve_on(versions, tax, uf, on_date)
        body["resolved"] = {
            "rate": float(resolved.rate) if resolved.rate is not None else None,
            "status": resolved.status,
            "isSimulationParameter": resolved.is_simulation,
        }
    body["items"] = [_item(row) for row in rows]
    record_audit(
        session,
        context=context,
        action="tax_rates.list",
        route="/v1/tax-rates",
        outcome="allowed",
        resource_type="tax_rate_versions",
    )
    return body
