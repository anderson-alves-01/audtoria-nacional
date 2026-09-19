from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import SourceRegistry, TaxCredit
from sirta_api.adapters.ingest.catalog_loader import catalog_source, catalog_sources
from sirta_api.application.audit import record_audit
from sirta_api.config import get_settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import assert_ingest_allowed, creates_tax_credit, ingest_allowed
from sirta_api.domain.errors import NotVisibleError

RUNTIME_STATUSES = frozenset({"ACTIVE", "SUSPENDED", "RETIRED"})


def _registry_payload(item: dict) -> dict:
    return {
        "name": item["name"],
        "maintainer": item["maintainer"],
        "official_url": item["official_url"],
        "source_role": item["source_role"],
        "access_classification": item["access_classification"],
        "status": item["status"],
        "purpose": item["purpose"],
        "legal_basis": item["legal_basis"],
        "license_terms": item["license_terms"],
        "layout_version": str(item.get("layout_version") or "none"),
        "fixture_kind": item["fixture_kind"],
        "notes": item.get("notes") or "",
    }


def _ensure_catalog(session: Session, *, context: AccessContext) -> None:
    existing_rows = {
        row.source_id: row
        for row in session.scalars(
            select(SourceRegistry).where(
                SourceRegistry.tenant_id == context.tenant_id,
                SourceRegistry.territory_id == context.territory_id,
            )
        ).all()
    }
    for item in catalog_sources():
        payload = _registry_payload(item)
        current = existing_rows.get(item["source_id"])
        if current is None:
            session.add(
                SourceRegistry(
                    id=uuid4(),
                    tenant_id=context.tenant_id,
                    territory_id=context.territory_id,
                    source_id=item["source_id"],
                    **payload,
                )
            )
            continue
        if current.status in RUNTIME_STATUSES:
            payload["status"] = current.status
        for field, value in payload.items():
            setattr(current, field, value)
    session.flush()


def _to_item(row: SourceRegistry) -> dict:
    catalog = catalog_source(row.source_id) or {}
    allowed = ingest_allowed(
        source_role=row.source_role,
        access_classification=row.access_classification,
        status=row.status,
        fixture_kind=row.fixture_kind,
        allow_synthetic_loads=get_settings().allow_synthetic_loads,
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
        "dataset": catalog.get("dataset"),
        "documentationUrl": catalog.get("documentation_url"),
        "competence": catalog.get("competence"),
        "granularity": catalog.get("granularity"),
        "authentication": catalog.get("authentication"),
        "personalData": catalog.get("personal_data"),
        "formula": catalog.get("formula"),
        "methodologyVersion": catalog.get("methodology_version"),
        "verifiedAt": catalog.get("verified_at"),
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
    official = any(row.fixture_kind == "OFFICIAL" for row in rows)
    return {
        "officialIngestion": official,
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
        allow_synthetic_loads=get_settings().allow_synthetic_loads,
    )
    catalog = catalog_source(source_id) or {}
    record_audit(
        session,
        context=context,
        action="catalog.dry_run",
        route=f"/v1/data-sources/{source_id}/dry-run",
        outcome="allowed",
        resource_type="source_registry",
        resource_id=row.id,
    )
    official = row.fixture_kind == "OFFICIAL"
    return {
        "sourceId": row.source_id,
        "dryRun": True,
        "wouldDownloadFullBase": official,
        "wouldCreateTaxCredit": False,
        "fixtureKind": row.fixture_kind,
        "endpoint": catalog.get("endpoint"),
        "dataset": catalog.get("dataset"),
    }
