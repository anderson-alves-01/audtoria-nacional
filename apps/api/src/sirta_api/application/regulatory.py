from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import GoldOfficial, GoldOfficialLine, RegulatoryItem
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.regulatory import (
    CATALOG_VERSION,
    PRESERVED_DOC_SOURCE_IDS,
    STATUS_NON_BINDING,
    SYNTHETIC_CATALOG,
)

DISCLAIMER = (
    "Non-binding catalog linked to preserved official documents when Gold exists. "
    "Official dates, rates and layouts require municipal and legal homologation "
    "before operational use. binding=false, operational=false, homologated=false."
)


def _ensure_catalog(session: Session, *, context: AccessContext) -> None:
    existing_codes = set(
        session.scalars(
            select(RegulatoryItem.code).where(
                RegulatoryItem.tenant_id == context.tenant_id,
                RegulatoryItem.territory_id == context.territory_id,
            )
        ).all()
    )
    for item in SYNTHETIC_CATALOG:
        if item.code in existing_codes:
            continue
        session.add(
            RegulatoryItem(
                id=uuid4(),
                tenant_id=context.tenant_id,
                territory_id=context.territory_id,
                code=item.code,
                title=item.title,
                source=item.source,
                version=item.version,
                kind=item.kind,
                affected_system=item.affected_system,
                status=STATUS_NON_BINDING,
                binding=False,
                notes=item.notes,
            )
        )
    session.flush()


def _preserved_documents(session: Session, *, context: AccessContext) -> list[dict]:
    docs: list[dict] = []
    for source_id in PRESERVED_DOC_SOURCE_IDS:
        gold = session.scalar(
            select(GoldOfficial)
            .where(
                GoldOfficial.tenant_id == context.tenant_id,
                GoldOfficial.territory_id == context.territory_id,
                GoldOfficial.source_id == source_id,
                GoldOfficial.published.is_(True),
            )
            .order_by(GoldOfficial.created_at.desc())
        )
        if gold is None:
            docs.append(
                {
                    "sourceId": source_id,
                    "published": False,
                    "methodologyVersion": None,
                    "officialUrl": None,
                    "bronzeSha256": None,
                    "checksumSha256": None,
                    "landingManifestPath": None,
                    "binding": False,
                    "operational": False,
                    "homologated": False,
                }
            )
            continue
        line = session.scalar(
            select(GoldOfficialLine)
            .where(GoldOfficialLine.gold_id == gold.id)
            .order_by(GoldOfficialLine.silver_row_id)
        )
        docs.append(
            {
                "sourceId": gold.source_id,
                "published": True,
                "methodologyVersion": gold.methodology_version,
                "officialUrl": gold.official_url,
                "bronzeSha256": line.bronze_sha256 if line is not None else None,
                "checksumSha256": line.checksum_sha256 if line is not None else None,
                "landingManifestPath": (line.landing_manifest_path if line is not None else None),
                "competence": gold.competence,
                "homologationStatus": gold.homologation_status,
                "runId": str(gold.run_id),
                "binding": False,
                "operational": False,
                "homologated": False,
            }
        )
    return docs


def list_ibs_cbs_calendar(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    _ensure_catalog(session, context=context)
    rows = session.scalars(
        select(RegulatoryItem)
        .where(
            RegulatoryItem.tenant_id == context.tenant_id,
            RegulatoryItem.territory_id == context.territory_id,
        )
        .order_by(RegulatoryItem.code)
    ).all()
    preserved = _preserved_documents(session, context=context)
    record_audit(
        session,
        context=context,
        action="regulatory.list",
        route="/v1/regulatory/ibs-cbs",
        outcome="allowed",
        resource_type="regulatory_calendar",
        resource_id=None,
    )
    return {
        "binding": False,
        "operational": False,
        "homologated": False,
        "disclaimer": DISCLAIMER,
        "catalogVersion": CATALOG_VERSION,
        "preservedDocuments": preserved,
        "items": [
            {
                "id": str(row.id),
                "code": row.code,
                "title": row.title,
                "source": row.source,
                "version": row.version,
                "kind": row.kind,
                "affectedSystem": row.affected_system,
                "status": row.status,
                "binding": row.binding,
                "notes": row.notes,
            }
            for row in rows
        ],
    }
