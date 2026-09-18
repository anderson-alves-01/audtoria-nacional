from datetime import UTC, datetime

from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import (
    AccessPurpose,
    Evidence,
    Organization,
    TaxCredit,
    TaxCreditEvidence,
    Tenant,
    Territory,
    User,
    UserTerritory,
)
from sirta_api.adapters.db.synthetic_ids import (
    CREDIT_ALPHA,
    CREDIT_BETA,
    EVIDENCE_ALPHA,
    EVIDENCE_ALPHA_SHA256,
    EVIDENCE_BETA,
    EVIDENCE_BETA_SHA256,
    ORG_PILOT,
    PURPOSE_ALPHA_ACTIVE,
    PURPOSE_ALPHA_EXPIRED,
    PURPOSE_BETA_ACTIVE,
    TAXPAYER_ALPHA,
    TAXPAYER_BETA,
    TENANT_ALPHA,
    TENANT_BETA,
    TERRITORY_ALPHA_CENTRO,
    TERRITORY_ALPHA_NORTE,
    TERRITORY_BETA_SEDE,
    USER_ADMIN_ALPHA,
    USER_ANALYST_ALPHA,
    USER_ANALYST_BETA,
    USER_COLLECTOR_ALPHA,
    USER_DEBT_ALPHA,
    USER_VALIDATOR_ALPHA,
)


def _ensure(session: Session, model, ident, **fields):
    row = session.get(model, ident)
    if row is None:
        payload = dict(fields)
        if isinstance(ident, tuple):
            session.add(model(**payload))
        else:
            session.add(model(id=ident, **payload))
        session.flush()


def seed_synthetic(session: Session) -> None:
    _ensure(session, Organization, ORG_PILOT, name="Municipio Sintetico")
    _ensure(
        session, Tenant, TENANT_ALPHA, organization_id=ORG_PILOT, slug="alpha", name="Tenant Alpha"
    )
    _ensure(
        session, Tenant, TENANT_BETA, organization_id=ORG_PILOT, slug="beta", name="Tenant Beta"
    )
    _ensure(
        session,
        Territory,
        TERRITORY_ALPHA_CENTRO,
        tenant_id=TENANT_ALPHA,
        code="centro",
        name="Centro",
    )
    _ensure(
        session,
        Territory,
        TERRITORY_ALPHA_NORTE,
        tenant_id=TENANT_ALPHA,
        code="norte",
        name="Norte",
    )
    _ensure(
        session, Territory, TERRITORY_BETA_SEDE, tenant_id=TENANT_BETA, code="sede", name="Sede"
    )
    users = (
        (USER_ANALYST_ALPHA, TENANT_ALPHA, "analyst.alpha", "analyst"),
        (USER_VALIDATOR_ALPHA, TENANT_ALPHA, "validator.alpha", "validator"),
        (USER_ADMIN_ALPHA, TENANT_ALPHA, "admin.alpha", "tech_admin"),
        (USER_COLLECTOR_ALPHA, TENANT_ALPHA, "collector.alpha", "collector"),
        (USER_DEBT_ALPHA, TENANT_ALPHA, "debt.alpha", "debt_officer"),
        (USER_ANALYST_BETA, TENANT_BETA, "analyst.beta", "analyst"),
    )
    for user_id, tenant_id, username, role in users:
        _ensure(
            session,
            User,
            user_id,
            tenant_id=tenant_id,
            subject=str(user_id),
            username=username,
            role=role,
        )
    links = (
        (USER_ANALYST_ALPHA, TERRITORY_ALPHA_CENTRO),
        (USER_VALIDATOR_ALPHA, TERRITORY_ALPHA_CENTRO),
        (USER_ADMIN_ALPHA, TERRITORY_ALPHA_CENTRO),
        (USER_COLLECTOR_ALPHA, TERRITORY_ALPHA_CENTRO),
        (USER_DEBT_ALPHA, TERRITORY_ALPHA_CENTRO),
        (USER_ANALYST_BETA, TERRITORY_BETA_SEDE),
    )
    for user_id, territory_id in links:
        _ensure(
            session,
            UserTerritory,
            (user_id, territory_id),
            user_id=user_id,
            territory_id=territory_id,
        )
    _ensure(
        session,
        AccessPurpose,
        PURPOSE_ALPHA_ACTIVE,
        tenant_id=TENANT_ALPHA,
        code="audit-iss",
        description="Synthetic ISS audit",
        expires_at=None,
    )
    _ensure(
        session,
        AccessPurpose,
        PURPOSE_ALPHA_EXPIRED,
        tenant_id=TENANT_ALPHA,
        code="expired-audit",
        description="Expired synthetic purpose",
        expires_at=datetime(2020, 1, 1, tzinfo=UTC),
    )
    _ensure(
        session,
        AccessPurpose,
        PURPOSE_BETA_ACTIVE,
        tenant_id=TENANT_BETA,
        code="audit-iss",
        description="Synthetic ISS audit beta",
        expires_at=None,
    )
    _ensure(
        session,
        Evidence,
        EVIDENCE_ALPHA,
        tenant_id=TENANT_ALPHA,
        sha256=EVIDENCE_ALPHA_SHA256,
        source="synthetic-ledger",
        media_type="text/plain",
    )
    _ensure(
        session,
        Evidence,
        EVIDENCE_BETA,
        tenant_id=TENANT_BETA,
        sha256=EVIDENCE_BETA_SHA256,
        source="synthetic-ledger",
        media_type="text/plain",
    )
    _ensure(
        session,
        TaxCredit,
        CREDIT_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
        taxpayer_id=TAXPAYER_ALPHA,
        tax_type="ISS",
        competence="2026-01",
        source_id="synthetic-ledger",
        principal_amount=1000,
        additional_amount=0,
        currency="BRL",
        calculation_memory="base 10000 * aliquota 0.10 = 1000",
        enforceability_status="ENFORCEABLE",
        created_by=USER_ANALYST_ALPHA,
    )
    _ensure(
        session,
        TaxCredit,
        CREDIT_BETA,
        tenant_id=TENANT_BETA,
        territory_id=TERRITORY_BETA_SEDE,
        purpose_id=PURPOSE_BETA_ACTIVE,
        taxpayer_id=TAXPAYER_BETA,
        tax_type="ISS",
        competence="2026-01",
        source_id="synthetic-ledger",
        principal_amount=2500,
        additional_amount=0,
        currency="BRL",
        calculation_memory="base 25000 * aliquota 0.10 = 2500",
        enforceability_status="ENFORCEABLE",
        created_by=USER_ANALYST_BETA,
    )
    _ensure(
        session,
        TaxCreditEvidence,
        (CREDIT_ALPHA, EVIDENCE_ALPHA),
        credit_id=CREDIT_ALPHA,
        evidence_id=EVIDENCE_ALPHA,
    )
    _ensure(
        session,
        TaxCreditEvidence,
        (CREDIT_BETA, EVIDENCE_BETA),
        credit_id=CREDIT_BETA,
        evidence_id=EVIDENCE_BETA,
    )


def run_seed() -> None:
    from sirta_api.adapters.db.session import get_session_factory

    session = get_session_factory()()
    try:
        seed_synthetic(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
