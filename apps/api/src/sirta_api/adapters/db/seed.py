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


def seed_synthetic(session: Session) -> None:
    session.add(Organization(id=ORG_PILOT, name="Municipio Sintetico"))
    session.flush()
    session.add_all(
        [
            Tenant(id=TENANT_ALPHA, organization_id=ORG_PILOT, slug="alpha", name="Tenant Alpha"),
            Tenant(id=TENANT_BETA, organization_id=ORG_PILOT, slug="beta", name="Tenant Beta"),
        ]
    )
    session.flush()
    session.add_all(
        [
            Territory(
                id=TERRITORY_ALPHA_CENTRO, tenant_id=TENANT_ALPHA, code="centro", name="Centro"
            ),
            Territory(id=TERRITORY_ALPHA_NORTE, tenant_id=TENANT_ALPHA, code="norte", name="Norte"),
            Territory(id=TERRITORY_BETA_SEDE, tenant_id=TENANT_BETA, code="sede", name="Sede"),
        ]
    )
    session.flush()
    session.add_all(
        [
            User(
                id=USER_ANALYST_ALPHA,
                tenant_id=TENANT_ALPHA,
                subject=str(USER_ANALYST_ALPHA),
                username="analyst.alpha",
                role="analyst",
            ),
            User(
                id=USER_VALIDATOR_ALPHA,
                tenant_id=TENANT_ALPHA,
                subject=str(USER_VALIDATOR_ALPHA),
                username="validator.alpha",
                role="validator",
            ),
            User(
                id=USER_ADMIN_ALPHA,
                tenant_id=TENANT_ALPHA,
                subject=str(USER_ADMIN_ALPHA),
                username="admin.alpha",
                role="tech_admin",
            ),
            User(
                id=USER_COLLECTOR_ALPHA,
                tenant_id=TENANT_ALPHA,
                subject=str(USER_COLLECTOR_ALPHA),
                username="collector.alpha",
                role="collector",
            ),
            User(
                id=USER_DEBT_ALPHA,
                tenant_id=TENANT_ALPHA,
                subject=str(USER_DEBT_ALPHA),
                username="debt.alpha",
                role="debt_officer",
            ),
            User(
                id=USER_ANALYST_BETA,
                tenant_id=TENANT_BETA,
                subject=str(USER_ANALYST_BETA),
                username="analyst.beta",
                role="analyst",
            ),
        ]
    )
    session.flush()
    session.add_all(
        [
            UserTerritory(user_id=USER_ANALYST_ALPHA, territory_id=TERRITORY_ALPHA_CENTRO),
            UserTerritory(user_id=USER_VALIDATOR_ALPHA, territory_id=TERRITORY_ALPHA_CENTRO),
            UserTerritory(user_id=USER_ADMIN_ALPHA, territory_id=TERRITORY_ALPHA_CENTRO),
            UserTerritory(user_id=USER_COLLECTOR_ALPHA, territory_id=TERRITORY_ALPHA_CENTRO),
            UserTerritory(user_id=USER_DEBT_ALPHA, territory_id=TERRITORY_ALPHA_CENTRO),
            UserTerritory(user_id=USER_ANALYST_BETA, territory_id=TERRITORY_BETA_SEDE),
        ]
    )
    session.flush()
    session.add_all(
        [
            AccessPurpose(
                id=PURPOSE_ALPHA_ACTIVE,
                tenant_id=TENANT_ALPHA,
                code="audit-iss",
                description="Synthetic ISS audit",
                expires_at=None,
            ),
            AccessPurpose(
                id=PURPOSE_ALPHA_EXPIRED,
                tenant_id=TENANT_ALPHA,
                code="expired-audit",
                description="Expired synthetic purpose",
                expires_at=datetime(2020, 1, 1, tzinfo=UTC),
            ),
            AccessPurpose(
                id=PURPOSE_BETA_ACTIVE,
                tenant_id=TENANT_BETA,
                code="audit-iss",
                description="Synthetic ISS audit beta",
                expires_at=None,
            ),
        ]
    )
    session.flush()
    session.add_all(
        [
            Evidence(
                id=EVIDENCE_ALPHA,
                tenant_id=TENANT_ALPHA,
                sha256=EVIDENCE_ALPHA_SHA256,
                source="synthetic-ledger",
                media_type="text/plain",
            ),
            Evidence(
                id=EVIDENCE_BETA,
                tenant_id=TENANT_BETA,
                sha256=EVIDENCE_BETA_SHA256,
                source="synthetic-ledger",
                media_type="text/plain",
            ),
        ]
    )
    session.flush()
    session.add_all(
        [
            TaxCredit(
                id=CREDIT_ALPHA,
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
            ),
            TaxCredit(
                id=CREDIT_BETA,
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
            ),
        ]
    )
    session.flush()
    session.add_all(
        [
            TaxCreditEvidence(credit_id=CREDIT_ALPHA, evidence_id=EVIDENCE_ALPHA),
            TaxCreditEvidence(credit_id=CREDIT_BETA, evidence_id=EVIDENCE_BETA),
        ]
    )
    session.flush()
