from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import SourceRegistry, TaxCredit
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import assert_ingest_allowed, creates_tax_credit, ingest_allowed
from sirta_api.domain.errors import NotVisibleError

SYNTHETIC_SOURCES = (
    {
        "source_id": "IBGE-SIDRA",
        "name": "IBGE/SIDRA indicadores territoriais",
        "maintainer": "IBGE",
        "official_url": "https://sidra.ibge.gov.br/",
        "source_role": "REFERENCE_ENRICHMENT",
        "access_classification": "PUBLIC_OPEN",
        "status": "APPROVED",
        "purpose": "Contexto econômico sintético",
        "legal_basis": "Dados abertos institucionais — catálogo local",
        "license_terms": "termos do órgão mantenedor",
        "layout_version": "catalog-synthetic-v1",
        "fixture_kind": "SYNTHETIC",
        "notes": "Metadados somente. Nenhuma base completa é baixada.",
    },
    {
        "source_id": "TESOURO-TRANSPARENTE",
        "name": "Tesouro Transparente — transferências",
        "maintainer": "Tesouro Nacional",
        "official_url": "https://www.tesourotransparente.gov.br/",
        "source_role": "OFFICIAL_TRANSFER",
        "access_classification": "PUBLIC_OPEN",
        "status": "APPROVED",
        "purpose": "Conciliação de transferências — catálogo",
        "legal_basis": "Publicação oficial — uso operacional G7 bloqueado",
        "license_terms": "termos do órgão mantenedor",
        "layout_version": "catalog-synthetic-v1",
        "fixture_kind": "SYNTHETIC",
        "notes": "Catálogo v0.5; conciliação oficial permanece OFFICIAL_BLOCKED.",
    },
    {
        "source_id": "PLANALTO-LEGISLACAO",
        "name": "Planalto — legislação",
        "maintainer": "Presidência da República",
        "official_url": "https://www.planalto.gov.br/",
        "source_role": "REGULATORY",
        "access_classification": "PUBLIC_OPEN",
        "status": "APPROVED",
        "purpose": "Catálogo regulatório versionado",
        "legal_basis": "Publicação oficial",
        "license_terms": "termos do órgão mantenedor",
        "layout_version": "catalog-synthetic-v1",
        "fixture_kind": "SYNTHETIC",
        "notes": "Não ativa regra IBS/CBS operacional.",
    },
    {
        "source_id": "MUNICIPAL-ISS-RESTRICTED",
        "name": "Arrecadação ISS municipal (restrita)",
        "maintainer": "Município piloto (não nomeado)",
        "official_url": "synthetic://blocked-municipal-iss",
        "source_role": "PRIMARY_FISCAL",
        "access_classification": "RESTRICTED",
        "status": "DISCOVERED",
        "purpose": "Constituição de crédito — bloqueado",
        "legal_basis": "Exige G0/G1 e autorização do controlador",
        "license_terms": "não aplicável até DPA",
        "layout_version": "none",
        "fixture_kind": "NONE",
        "notes": "Interface de catálogo apenas. Ingestão real proibida.",
    },
)


def _ensure_catalog(session: Session, *, context: AccessContext) -> None:
    existing = set(
        session.scalars(
            select(SourceRegistry.source_id).where(
                SourceRegistry.tenant_id == context.tenant_id,
                SourceRegistry.territory_id == context.territory_id,
            )
        ).all()
    )
    for item in SYNTHETIC_SOURCES:
        if item["source_id"] in existing:
            continue
        session.add(
            SourceRegistry(
                id=uuid4(),
                tenant_id=context.tenant_id,
                territory_id=context.territory_id,
                **item,
            )
        )
    session.flush()


def _to_item(row: SourceRegistry) -> dict:
    allowed = ingest_allowed(
        source_role=row.source_role,
        access_classification=row.access_classification,
        status=row.status,
        fixture_kind=row.fixture_kind,
    )
    return {
        "id": str(row.id),
        "sourceId": row.source_id,
        "name": row.name,
        "maintainer": row.maintainer,
        "officialUrl": row.official_url,
        "sourceRole": row.source_role,
        "accessClassification": row.access_classification,
        "status": row.status,
        "purpose": row.purpose,
        "legalBasis": row.legal_basis,
        "licenseTerms": row.license_terms,
        "layoutVersion": row.layout_version,
        "fixtureKind": row.fixture_kind,
        "ingestAllowed": allowed,
        "createsTaxCredit": creates_tax_credit(row.source_role),
        "notes": row.notes,
    }


def list_sources(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    credits_before = session.scalar(
        select(func.count()).select_from(TaxCredit).where(TaxCredit.tenant_id == context.tenant_id)
    )
    _ensure_catalog(session, context=context)
    rows = session.scalars(
        select(SourceRegistry)
        .where(
            SourceRegistry.tenant_id == context.tenant_id,
            SourceRegistry.territory_id == context.territory_id,
        )
        .order_by(SourceRegistry.source_id)
    ).all()
    credits_after = session.scalar(
        select(func.count()).select_from(TaxCredit).where(TaxCredit.tenant_id == context.tenant_id)
    )
    record_audit(
        session,
        context=context,
        action="catalog.list",
        route="/v1/data-sources",
        outcome="allowed",
        resource_type="source_registry",
    )
    return {
        "officialIngestion": False,
        "taxCreditCreated": int(credits_after or 0) != int(credits_before or 0),
        "items": [_to_item(row) for row in rows],
    }


def dry_run_source(session: Session, *, context: AccessContext, source_id: str) -> dict:
    context.ensure_fiscal_read()
    _ensure_catalog(session, context=context)
    row = session.scalar(
        select(SourceRegistry).where(
            SourceRegistry.tenant_id == context.tenant_id,
            SourceRegistry.territory_id == context.territory_id,
            SourceRegistry.source_id == source_id,
        )
    )
    if row is None:
        raise NotVisibleError()
    assert_ingest_allowed(
        source_role=row.source_role,
        access_classification=row.access_classification,
        status=row.status,
        fixture_kind=row.fixture_kind,
    )
    record_audit(
        session,
        context=context,
        action="catalog.dry_run",
        route=f"/v1/data-sources/{source_id}/dry-run",
        outcome="allowed",
        resource_type="source_registry",
        resource_id=row.id,
    )
    return {
        "sourceId": row.source_id,
        "dryRun": True,
        "wouldDownloadFullBase": False,
        "wouldCreateTaxCredit": False,
        "fixtureKind": row.fixture_kind,
    }
