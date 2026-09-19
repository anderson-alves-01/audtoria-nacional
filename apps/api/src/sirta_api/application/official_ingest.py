from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import DataLoadRow, DataLoadRun, GoldOfficial, SourceRegistry
from sirta_api.adapters.ingest.catalog_loader import catalog_source, load_official_catalog
from sirta_api.adapters.ingest.http_client import OfficialHttpClient, OfficialHttpResponse
from sirta_api.adapters.ingest.parsers import (
    landing_dir,
    minimize_row,
    parse_ibge_sidra_series,
    parse_official_document,
    parse_siconfi_entes,
    parse_tesouro_transfer_types,
    sha256_bytes,
    write_landing,
)
from sirta_api.application.audit import record_audit
from sirta_api.config import get_settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import (
    HOMOLOGATION_PENDING,
    OFFICIAL_BANNER,
    assert_ingest_allowed,
)
from sirta_api.domain.errors import ConflictError, ForbiddenError

PARSERS = {
    "ibge_sidra_series": parse_ibge_sidra_series,
    "siconfi_entes": parse_siconfi_entes,
    "tesouro_transfer_types": parse_tesouro_transfer_types,
}


def ingest_official_source(
    session: Session,
    *,
    context: AccessContext,
    source: SourceRegistry,
    catalog: dict,
    http_client: OfficialHttpClient,
) -> dict:
    if context.role.value != "tech_admin":
        raise ForbiddenError("Only a technical administrator may run data loads")
    assert_ingest_allowed(
        source_role=source.source_role,
        access_classification=source.access_classification,
        status=source.status,
        fixture_kind=source.fixture_kind,
    )
    connector = str(catalog.get("connector") or "")
    endpoint = str(catalog.get("endpoint") or "")
    if connector in {"", "none"} or endpoint in {"", "none"}:
        raise ForbiddenError("Official connector is not activated for this source")
    timeout = get_settings().official_http_timeout_seconds
    try:
        fetched = _fetch_pages(http_client, endpoint=endpoint, connector=connector, timeout=timeout)
    except Exception as exc:
        source.status = "UNAVAILABLE"
        session.flush()
        return {
            "runId": None,
            "sourceId": source.source_id,
            "status": "UNAVAILABLE",
            "checksum": None,
            "receivedCount": 0,
            "silverCount": 0,
            "quarantinedCount": 0,
            "landingPreserved": False,
            "published": False,
            "replay": False,
            "taxCreditCreated": False,
            "wouldDownloadFullBase": True,
            "error": str(exc),
        }
    if fetched.status_code >= 400:
        source.status = "UNAVAILABLE"
        session.flush()
        return {
            "runId": None,
            "sourceId": source.source_id,
            "status": "UNAVAILABLE",
            "checksum": None,
            "receivedCount": 0,
            "silverCount": 0,
            "quarantinedCount": 0,
            "landingPreserved": False,
            "published": False,
            "replay": False,
            "taxCreditCreated": False,
            "wouldDownloadFullBase": True,
            "httpStatus": fetched.status_code,
        }
    digest = sha256_bytes(fetched.body)
    layout = str(catalog.get("layout_version") or source.layout_version)
    existing = session.scalar(
        select(DataLoadRun).where(
            DataLoadRun.tenant_id == context.tenant_id,
            DataLoadRun.checksum == digest,
            DataLoadRun.layout_version == layout,
        )
    )
    if existing is not None:
        return _body(existing, source=source, catalog=catalog, replay=True)
    extracted_at = datetime.now(UTC)
    silver, quarantined = _parse(connector, fetched)
    if connector == "siconfi_entes":
        silver = [minimize_row(row) for row in silver]
        for row, _reason in quarantined:
            row.pop("cnpj", None)
    datalake = Path(get_settings().datalake_root)
    directory = landing_dir(
        root=datalake,
        source_id=source.source_id,
        dataset=str(catalog.get("dataset") or source.source_id),
        extracted_at=extracted_at,
        checksum=digest,
    )
    manifest = {
        "sourceId": source.source_id,
        "dataset": catalog.get("dataset"),
        "officialUrl": catalog.get("official_url"),
        "logicalUrl": endpoint,
        "resolvedUrl": fetched.url,
        "extractedAtUtc": extracted_at.isoformat(),
        "httpStatus": fetched.status_code,
        "etag": fetched.etag,
        "lastModified": fetched.last_modified,
        "contentType": fetched.content_type,
        "sha256": digest,
        "bytes": len(fetched.body),
        "competence": catalog.get("competence"),
        "coverage": catalog.get("granularity"),
        "layoutVersion": layout,
        "receivedCount": len(silver) + len(quarantined),
        "silverCount": len(silver),
        "quarantinedCount": len(quarantined),
    }
    write_landing(directory=directory, body=fetched.body, manifest=manifest)
    competence = str(catalog.get("competence") or "2026")[:7]
    quality = "TECHNICALLY_VALIDATED" if silver else "QUARANTINED"
    status = "PUBLISHED" if silver else "QUARANTINED"
    run = DataLoadRun(
        id=uuid4(),
        tenant_id=context.tenant_id,
        territory_id=context.territory_id,
        source_id=source.source_id,
        layout_version=layout,
        competence=competence,
        checksum=digest,
        status=status,
        received_count=len(silver) + len(quarantined),
        silver_count=len(silver),
        quarantined_count=len(quarantined),
        published=bool(silver),
        created_at=extracted_at,
    )
    session.add(run)
    session.flush()
    session.add(
        DataLoadRow(
            run_id=run.id,
            row_id="landing-manifest",
            layer="landing",
            status="PRESERVED",
            payload={
                "path": str(directory / "payload.bin"),
                "manifestPath": str(directory / "manifest.json"),
                **manifest,
            },
        )
    )
    session.add(
        DataLoadRow(
            run_id=run.id,
            row_id="bronze-object",
            layer="bronze",
            status="IMMUTABLE",
            payload={
                "sha256": digest,
                "bytes": len(fetched.body),
                "logicalUrl": endpoint,
                "httpStatus": fetched.status_code,
            },
        )
    )
    for row in silver:
        session.add(
            DataLoadRow(
                run_id=run.id,
                row_id=str(row["rowId"])[:64],
                layer="silver",
                status="VALIDATED",
                payload=minimize_row(row),
            )
        )
    for row, reason in quarantined:
        session.add(
            DataLoadRow(
                run_id=run.id,
                row_id=str(row.get("rowId") or "unknown")[:64],
                layer="quarantine",
                status="QUARANTINED",
                payload=minimize_row(row),
                reason=reason,
            )
        )
    numeric_values = [
        float(row["value"]) for row in silver if isinstance(row.get("value"), (int, float))
    ]
    gold = GoldOfficial(
        tenant_id=context.tenant_id,
        territory_id=context.territory_id,
        run_id=run.id,
        source_id=source.source_id,
        source_role=source.source_role,
        dataset=str(catalog.get("dataset") or source.source_id),
        maintainer=source.maintainer,
        official_url=str(catalog.get("official_url") or source.official_url),
        indicator=str(catalog.get("indicator") or source.source_id),
        formula=str(catalog.get("formula") or ""),
        methodology_version=str(catalog.get("methodology_version") or layout),
        competence=competence,
        granularity=str(catalog.get("granularity") or "unknown"),
        quality_level=quality,
        homologation_status=HOMOLOGATION_PENDING,
        coverage_count=len(silver),
        silver_row_count=len(silver),
        quarantined_count=len(quarantined),
        numeric_total=sum(numeric_values) if numeric_values else None,
        lineage={
            "bronzeSha256": digest,
            "landingPath": str(directory),
            "endpoint": endpoint,
            "httpStatus": fetched.status_code,
        },
        published=bool(silver),
        created_at=extracted_at,
    )
    session.add(gold)
    if silver:
        source.status = "ACTIVE"
    record_audit(
        session,
        context=context,
        action="catalog.official_ingest",
        route=f"/v1/data-sources/{source.source_id}/ingest",
        outcome="allowed",
        resource_type="data_load_run",
        resource_id=run.id,
    )
    session.flush()
    return _body(run, source=source, catalog=catalog, replay=False)


def published_official_enrichment(
    session: Session, *, context: AccessContext, source_id: str
) -> dict:
    context.ensure_fiscal_read()
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
    catalog = catalog_source(source_id) or {}
    if gold is None:
        reason = str(catalog.get("notes") or "Nenhum Gold oficial publicado para esta fonte.")
        return {
            "sourceId": source_id,
            "published": False,
            "indicatorCount": 0,
            "silverRowCount": 0,
            "quarantinedCount": 0,
            "createsTaxCredit": False,
            "homologationStatus": HOMOLOGATION_PENDING,
            "banner": OFFICIAL_BANNER,
            "emptyReason": reason,
            "note": reason,
        }
    return {
        "sourceId": gold.source_id,
        "sourceRole": gold.source_role,
        "published": True,
        "indicatorCount": gold.silver_row_count,
        "silverRowCount": gold.silver_row_count,
        "quarantinedCount": gold.quarantined_count,
        "createsTaxCredit": False,
        "methodologyVersion": gold.methodology_version,
        "formula": gold.formula,
        "dataset": gold.dataset,
        "maintainer": gold.maintainer,
        "officialUrl": gold.official_url,
        "competence": gold.competence,
        "granularity": gold.granularity,
        "qualityLevel": gold.quality_level,
        "homologationStatus": gold.homologation_status,
        "numericTotal": float(gold.numeric_total) if gold.numeric_total is not None else None,
        "lineage": gold.lineage,
        "runId": str(gold.run_id),
        "banner": OFFICIAL_BANNER,
        "note": OFFICIAL_BANNER,
    }


def list_official_gold(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    catalog = load_official_catalog()
    rows = session.scalars(
        select(GoldOfficial)
        .where(
            GoldOfficial.tenant_id == context.tenant_id,
            GoldOfficial.territory_id == context.territory_id,
            GoldOfficial.published.is_(True),
        )
        .order_by(GoldOfficial.source_id)
    ).all()
    items = []
    published_ids = {row.source_id for row in rows}
    for row in rows:
        items.append(
            {
                "sourceId": row.source_id,
                "indicator": row.indicator,
                "maintainer": row.maintainer,
                "dataset": row.dataset,
                "competence": row.competence,
                "lastExtractedAt": row.created_at.isoformat(),
                "formula": row.formula,
                "methodologyVersion": row.methodology_version,
                "coverageCount": row.coverage_count,
                "qualityLevel": row.quality_level,
                "homologationStatus": row.homologation_status,
                "officialUrl": row.official_url,
                "lineage": row.lineage,
                "quarantinedCount": row.quarantined_count,
                "numericTotal": float(row.numeric_total) if row.numeric_total is not None else None,
                "createsTaxCredit": False,
            }
        )
    empty = []
    for source in catalog["sources"]:
        source_id = source["source_id"]
        if source_id in published_ids:
            continue
        empty.append(
            {
                "sourceId": source_id,
                "status": source.get("status"),
                "emptyReason": source.get("notes"),
                "officialUrl": source.get("official_url"),
            }
        )
    return {
        "banner": catalog.get("banner") or OFFICIAL_BANNER,
        "homologationStatus": catalog.get("homologation_status") or HOMOLOGATION_PENDING,
        "createsTaxCredit": False,
        "published": bool(items),
        "items": items,
        "emptySources": empty,
    }


def _parse(
    connector: str, fetched: OfficialHttpResponse
) -> tuple[list[dict], list[tuple[dict, str]]]:
    if connector == "official_document":
        return parse_official_document(
            fetched.body, content_type=fetched.content_type, url=fetched.url
        )
    parser = PARSERS.get(connector)
    if parser is None:
        raise ConflictError("Official connector is not implemented")
    return parser(fetched.body)


def _fetch_pages(
    client: OfficialHttpClient, *, endpoint: str, connector: str, timeout: float
) -> OfficialHttpResponse:
    first = client.fetch(endpoint, timeout=timeout)
    if connector != "siconfi_entes" or first.status_code >= 400:
        return first
    try:
        payload = json.loads(first.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return first
    if not isinstance(payload, dict) or not payload.get("hasMore"):
        return first
    items = list(payload.get("items") or [])
    offset = int(payload.get("offset") or 0) + int(payload.get("limit") or len(items) or 1)
    while True:
        page = client.fetch(f"{endpoint}?offset={offset}&limit=1000", timeout=timeout)
        if page.status_code >= 400:
            break
        try:
            body = json.loads(page.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            break
        items.extend(body.get("items") or [])
        if not body.get("hasMore"):
            break
        offset = int(body.get("offset") or offset) + int(body.get("limit") or 1000)
    merged = json.dumps(
        {**payload, "items": items, "hasMore": False, "count": len(items)},
        ensure_ascii=False,
    ).encode("utf-8")
    return OfficialHttpResponse(
        url=first.url,
        status_code=first.status_code,
        body=merged,
        etag=first.etag,
        last_modified=first.last_modified,
        content_type=first.content_type,
    )


def _body(run: DataLoadRun, *, source: SourceRegistry, catalog: dict, replay: bool) -> dict:
    return {
        "runId": str(run.id),
        "sourceId": source.source_id,
        "status": run.status,
        "checksum": run.checksum,
        "receivedCount": run.received_count,
        "silverCount": run.silver_count,
        "quarantinedCount": run.quarantined_count,
        "landingPreserved": True,
        "published": run.published,
        "replay": replay,
        "taxCreditCreated": False,
        "wouldDownloadFullBase": True,
        "homologationStatus": HOMOLOGATION_PENDING,
        "dataset": catalog.get("dataset"),
        "officialUrl": catalog.get("official_url") or source.official_url,
        "banner": OFFICIAL_BANNER,
    }
