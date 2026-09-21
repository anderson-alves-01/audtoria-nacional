from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import (
    DataLoadRow,
    DataLoadRun,
    GoldOfficial,
    GoldOfficialLine,
    IngestCheckpoint,
    SourceRegistry,
)
from sirta_api.adapters.ingest.catalog_loader import catalog_source, load_official_catalog
from sirta_api.adapters.ingest.http_client import OfficialHttpClient, OfficialHttpResponse
from sirta_api.adapters.ingest.parsers import (
    landing_dir,
    minimize_row,
    normalize_place,
    parse_anatel_dados_gov,
    parse_aneel_ckan_open,
    parse_anp_revendedores_api,
    parse_bcb_olinda_expectativas,
    parse_bcb_sgs_olinda,
    parse_cnes_datasus_open,
    parse_epe_open_files,
    parse_ibge_sidra_series,
    parse_official_document,
    parse_siconfi_entes,
    parse_siconfi_statement,
    parse_state_ac_csv,
    parse_state_ac_transparencia_json,
    parse_state_al_xls,
    parse_state_ba_csv,
    parse_state_ce_xls,
    parse_state_es_csv,
    parse_state_go_csv,
    parse_state_go_economia_xlsx,
    parse_state_ma_xls,
    parse_state_mg_csv,
    parse_state_ms_csv,
    parse_state_pa_icms_verde_xlsx,
    parse_state_pe_csv,
    parse_state_pi_repasseweb_html,
    parse_state_pr_html,
    parse_state_rn_xls,
    parse_state_ro_csv,
    parse_state_rs_xls,
    parse_tesouro_coint_municipio_csv,
    parse_tesouro_monthly_csv,
    parse_tesouro_transfer_types,
    sha256_bytes,
    write_landing,
)
from sirta_api.adapters.observability.ingest_events import (
    log_ingest_finished,
    log_ingest_started,
)
from sirta_api.application.audit import record_audit
from sirta_api.config import get_settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.backfill_controls import (
    assert_datalake_space,
    build_backfill_metrics,
    checkpoint_status_after_slice,
    clamp_max_entes,
    resolve_fpm_endpoint,
    select_entes_slice,
    statement_partition_key,
)
from sirta_api.domain.catalog import (
    HOMOLOGATION_PENDING,
    OFFICIAL_BANNER,
    assert_ingest_allowed,
)
from sirta_api.domain.errors import ConflictError, ForbiddenError
from sirta_api.domain.gold import (
    assert_gold_lineage_complete,
    coverage_divergence,
    presentation_for,
)
from sirta_api.domain.rfb_cnpj import (
    RFB_CONNECTOR,
    assert_territorial_scope_ready,
    build_rfb_readiness,
)

PARSERS = {
    "ibge_sidra_series": parse_ibge_sidra_series,
    "siconfi_entes": parse_siconfi_entes,
    "tesouro_transfer_types": parse_tesouro_transfer_types,
    "tesouro_monthly_csv": parse_tesouro_monthly_csv,
    "tesouro_coint_municipio_csv": parse_tesouro_coint_municipio_csv,
    "siconfi_statement": parse_siconfi_statement,
    "state_pe_csv": parse_state_pe_csv,
    "state_ba_csv": parse_state_ba_csv,
    "state_mg_csv": parse_state_mg_csv,
    "state_es_csv": parse_state_es_csv,
    "state_go_csv": parse_state_go_csv,
    "state_go_economia_xlsx": parse_state_go_economia_xlsx,
    "state_ms_csv": parse_state_ms_csv,
    "state_ro_csv": parse_state_ro_csv,
    "state_ac_csv": parse_state_ac_csv,
    "state_ac_transparencia_json": parse_state_ac_transparencia_json,
    "state_pi_repasseweb_html": parse_state_pi_repasseweb_html,
    "state_pr_html": parse_state_pr_html,
    "state_pa_icms_verde_xlsx": parse_state_pa_icms_verde_xlsx,
    "state_al_xls": parse_state_al_xls,
    "state_ce_xls": parse_state_ce_xls,
    "state_ma_xls": parse_state_ma_xls,
    "state_rn_xls": parse_state_rn_xls,
    "state_rs_xls": parse_state_rs_xls,
    "anp_revendedores_api": parse_anp_revendedores_api,
    "aneel_ckan_open": parse_aneel_ckan_open,
    "anatel_dados_gov": parse_anatel_dados_gov,
    "bcb_sgs_olinda": parse_bcb_sgs_olinda,
    "bcb_olinda_expectativas": parse_bcb_olinda_expectativas,
    "epe_open_files": parse_epe_open_files,
    "cnes_datasus_open": parse_cnes_datasus_open,
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
    connector = str(catalog.get("connector") or "")
    endpoint = str(catalog.get("endpoint") or "")
    if connector == RFB_CONNECTOR:
        assert_territorial_scope_ready(catalog.get("parameters"))
    assert_ingest_allowed(
        source_role=source.source_role,
        access_classification=source.access_classification,
        status=source.status,
        fixture_kind=source.fixture_kind,
    )
    if connector == RFB_CONNECTOR:
        raise ForbiddenError(
            "RFB CNPJ territorial connector is ready but national/runtime load "
            "remains blocked until TECHNICALLY_APPROVED scoped publication"
        )
    if connector in {
        "restricted_upload",
        "state_transfer_adapter",
        "portal_transparencia_api",
    }:
        raise ForbiddenError("Official connector is waiting territorial scope or credentials")
    if connector in {"", "none"} or endpoint in {"", "none"}:
        raise ForbiddenError("Official connector is not activated for this source")
    log_ingest_started(
        source_id=source.source_id,
        tenant_id=str(context.tenant_id),
        territory_id=str(context.territory_id),
    )
    timeout = get_settings().official_http_timeout_seconds
    try:
        fetched = _fetch_source(
            http_client,
            catalog=catalog,
            connector=connector,
            endpoint=endpoint,
            timeout=timeout,
            session=session,
            context=context,
            source_id=source.source_id,
        )
    except (ConflictError, ForbiddenError):
        raise
    except Exception as exc:
        source.status = "UNAVAILABLE"
        session.flush()
        body = {
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
        log_ingest_finished(
            outcome="unavailable",
            source_id=source.source_id,
            tenant_id=str(context.tenant_id),
            territory_id=str(context.territory_id),
            run_id=None,
            received_count=0,
            silver_count=0,
            quarantined_count=0,
            error=str(exc),
        )
        return body
    if fetched.status_code >= 400:
        source.status = "UNAVAILABLE"
        session.flush()
        body = {
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
        log_ingest_finished(
            outcome="unavailable",
            source_id=source.source_id,
            tenant_id=str(context.tenant_id),
            territory_id=str(context.territory_id),
            run_id=None,
            received_count=0,
            silver_count=0,
            quarantined_count=0,
            http_status=fetched.status_code,
            error=f"http_status_{fetched.status_code}",
        )
        return body
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
        body = _body(existing, source=source, catalog=catalog, replay=True)
        log_ingest_finished(
            outcome="replay",
            source_id=source.source_id,
            tenant_id=str(context.tenant_id),
            territory_id=str(context.territory_id),
            run_id=body["runId"],
            received_count=body["receivedCount"],
            silver_count=body["silverCount"],
            quarantined_count=body["quarantinedCount"],
        )
        return body
    extracted_at = datetime.now(UTC)
    silver, quarantined = _parse(
        connector,
        fetched,
        session=session,
        context=context,
        catalog=catalog,
        http_client=http_client,
    )
    if connector == "siconfi_entes":
        silver = [minimize_row(row) for row in silver]
        for row, _reason in quarantined:
            row.pop("cnpj", None)
    settings = get_settings()
    datalake = Path(settings.datalake_root)
    disk_free = assert_datalake_space(
        root=datalake,
        min_free_bytes=settings.datalake_min_free_bytes,
        required_bytes=len(fetched.body),
    )
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
        "diskFreeBytes": disk_free,
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
        float(row["value"])
        for row in silver
        if isinstance(row.get("value"), (int, float))
        and presentation_for(source.source_id)["valueKind"]
        in {"REFERENCE_QUANTITY", "TRANSFER_AMOUNT_AS_PUBLISHED"}
        and str(row.get("variableId") or "") != "6575"
        and row.get("modality")
        in {
            None,
            "FPM_RECEIVED",
            "ITR_RECEIVED",
            "IPI_EXP_RECEIVED",
            "ROYALTY_RECEIVED",
            "ICMS_QUOTA",
            "IPVA_QUOTA",
            "IPI_QUOTA",
            "CIDE_QUOTA",
            "ROYALTY_QUOTA",
        }
    ]
    presentation = presentation_for(source.source_id)
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
            "landingManifestPath": str(directory / "manifest.json"),
            "endpoint": endpoint,
            "httpStatus": fetched.status_code,
            "valueKind": presentation["valueKind"],
            "presentation": presentation["label"],
            "createsTaxCredit": False,
        },
        published=bool(silver),
        created_at=extracted_at,
    )
    session.add(gold)
    session.flush()
    for row in silver:
        line = {
            "silverRowId": str(row["rowId"])[:64],
            "bronzeSha256": digest,
            "checksumSha256": digest,
            "landingManifestPath": str(directory / "manifest.json"),
            "officialUrl": str(catalog.get("official_url") or source.official_url),
            "ibgeCode": row.get("ibgeCode"),
            "value": row.get("value"),
            "unit": row.get("unit"),
        }
        assert_gold_lineage_complete(line)
        session.add(
            GoldOfficialLine(
                gold_id=gold.id,
                run_id=run.id,
                source_id=source.source_id,
                silver_row_id=line["silverRowId"],
                bronze_sha256=digest,
                checksum_sha256=digest,
                landing_manifest_path=line["landingManifestPath"],
                official_url=line["officialUrl"],
                ibge_code=str(row.get("ibgeCode") or "")[:7] or None,
                value=float(row["value"]) if isinstance(row.get("value"), (int, float)) else None,
                unit=str(row.get("unit") or "")[:32] or None,
                payload=minimize_row(row),
            )
        )
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
    body = _body(run, source=source, catalog=catalog, replay=False)
    log_ingest_finished(
        outcome="success",
        source_id=source.source_id,
        tenant_id=str(context.tenant_id),
        territory_id=str(context.territory_id),
        run_id=body["runId"],
        received_count=body["receivedCount"],
        silver_count=body["silverCount"],
        quarantined_count=body["quarantinedCount"],
    )
    return body


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
    line_counts = {
        gold_id: count
        for gold_id, count in session.execute(
            select(GoldOfficialLine.gold_id, func.count(GoldOfficialLine.id)).group_by(
                GoldOfficialLine.gold_id
            )
        )
    }
    for row in rows:
        presentation = presentation_for(row.source_id)
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
                "valueKind": presentation["valueKind"],
                "presentation": presentation["label"],
                "financial": presentation["financial"],
                "lineageLineCount": int(line_counts.get(row.id) or 0),
            }
        )
    divergence = coverage_divergence(items)
    if divergence is not None:
        items.append(divergence)
    empty = []
    for source in catalog["sources"]:
        source_id = source["source_id"]
        if source_id in published_ids:
            continue
        empty.append(
            {
                "sourceId": source_id,
                "status": source.get("status"),
                "emptyReason": source.get("notes")
                or f"Sem Gold oficial publicado para {source_id}.",
                "officialUrl": source.get("official_url"),
                "competence": source.get("competence"),
                "formula": source.get("formula"),
                "qualityLevel": source.get("status"),
                "homologationStatus": HOMOLOGATION_PENDING,
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


def list_official_gold_lines(
    session: Session, *, context: AccessContext, source_id: str | None = None
) -> dict:
    context.ensure_fiscal_read()
    query = (
        select(GoldOfficialLine)
        .join(GoldOfficial, GoldOfficialLine.gold_id == GoldOfficial.id)
        .where(
            GoldOfficial.tenant_id == context.tenant_id,
            GoldOfficial.territory_id == context.territory_id,
            GoldOfficial.published.is_(True),
        )
    )
    if source_id:
        query = query.where(GoldOfficialLine.source_id == source_id)
    rows = session.scalars(
        query.order_by(GoldOfficialLine.source_id, GoldOfficialLine.silver_row_id)
    ).all()
    items = []
    for row in rows:
        line = {
            "sourceId": row.source_id,
            "silverRowId": row.silver_row_id,
            "bronzeSha256": row.bronze_sha256,
            "checksumSha256": row.checksum_sha256,
            "landingManifestPath": row.landing_manifest_path,
            "officialUrl": row.official_url,
            "ibgeCode": row.ibge_code,
            "value": float(row.value) if row.value is not None else None,
            "unit": row.unit,
        }
        assert_gold_lineage_complete(line)
        items.append({**line, "payload": row.payload})
    return {
        "banner": OFFICIAL_BANNER,
        "homologationStatus": HOMOLOGATION_PENDING,
        "createsTaxCredit": False,
        "items": items,
    }


def _parse(
    connector: str,
    fetched: OfficialHttpResponse,
    *,
    session: Session,
    context: AccessContext,
    catalog: dict,
    http_client: OfficialHttpClient | None = None,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    if connector == "official_document":
        return parse_official_document(
            fetched.body, content_type=fetched.content_type, url=fetched.url
        )
    parser = PARSERS.get(connector)
    if parser is None:
        raise ConflictError("Official connector is not implemented")
    if connector == "tesouro_monthly_csv":
        parameters = catalog.get("parameters") or {}
        item_allowlist = parameters.get("transfer_item_allowlist")
        destination_allowlist = parameters.get("transfer_destination_allowlist")
        return parser(
            fetched.body,
            ibge_lookup=_ibge_lookup(session, context=context),
            item_allowlist=list(item_allowlist) if item_allowlist else None,
            destination_allowlist=(list(destination_allowlist) if destination_allowlist else None),
            transfer_name=(
                str(parameters.get("transfer_name")) if parameters.get("transfer_name") else None
            ),
        )
    if connector == "tesouro_coint_municipio_csv":
        parameters = catalog.get("parameters") or {}
        max_rows = parameters.get("max_rows")
        return parser(
            fetched.body,
            ibge_lookup=_ibge_lookup(session, context=context),
            transfer_name=str(parameters.get("transfer_name") or catalog.get("name") or "TRANSFER"),
            competence=str(parameters.get("competence") or catalog.get("competence") or ""),
            max_rows=int(max_rows) if max_rows is not None else None,
        )
    if connector == "state_pe_csv":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "PE"),
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_ba_csv":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "BA"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2024"),
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_mg_csv":
        parameters = catalog.get("parameters") or {}
        municipio_body, tempo_body = _fetch_mg_dims(
            client=http_client,
            catalog=catalog,
            timeout=get_settings().official_http_timeout_seconds,
        )
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "MG"),
            competence_year=str(
                parameters.get("competence_year") or catalog.get("competence") or "2024"
            )[:4],
            municipio_dim=municipio_body,
            tempo_dim=tempo_body,
        )
    if connector == "state_es_csv":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "ES"),
            competence_year=str(
                parameters.get("competence_year") or catalog.get("competence") or "2024"
            )[:4],
        )
    if connector == "state_go_csv":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "IPVA"),
            uf=str(parameters.get("uf") or "GO"),
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_go_economia_xlsx":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "GO"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2024-11")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_ms_csv":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "MS"),
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_ro_csv":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "RO"),
            competence_year=str(
                parameters.get("competence_year") or catalog.get("competence") or "2022"
            )[:4],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_ac_csv":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "AC"),
            competence_year=str(
                parameters.get("competence_year") or catalog.get("competence") or "2021"
            )[:4],
        )
    if connector == "state_ac_transparencia_json":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "IPVA"),
            uf=str(parameters.get("uf") or "AC"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2025-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_pi_repasseweb_html":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "IPVA"),
            uf=str(parameters.get("uf") or "PI"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2025-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_pr_html":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "PR"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2025-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_pa_icms_verde_xlsx":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            uf=str(parameters.get("uf") or "PA"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2024-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_al_xls":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "AL"),
            competence_year=str(
                parameters.get("competence_year") or catalog.get("competence") or "2021"
            )[:4],
        )
    if connector == "state_ce_xls":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "CE"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2025-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_ma_xls":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "MA"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2026-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_rn_xls":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "RN"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2026-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "state_rs_xls":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            tax=str(parameters.get("tax") or "ICMS"),
            uf=str(parameters.get("uf") or "RS"),
            competence=str(parameters.get("competence") or catalog.get("competence") or "2025-01")[
                :7
            ],
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "anp_revendedores_api":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            uf=str(parameters.get("uf") or ""),
            competence=str(
                parameters.get("competence") or catalog.get("competence") or "as_published"
            ),
            ibge_lookup=_ibge_lookup(session, context=context),
        )
    if connector == "aneel_ckan_open":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            uf=str(parameters.get("uf") or ""),
            competence=str(
                parameters.get("competence") or catalog.get("competence") or "as_published"
            ),
        )
    if connector == "bcb_sgs_olinda":
        return _parse_bcb_sgs_allowlist(
            fetched,
            catalog=catalog,
            http_client=http_client,
            parser=parser,
        )
    if connector == "bcb_olinda_expectativas":
        return _parse_bcb_olinda_expectativas_allowlist(
            fetched,
            catalog=catalog,
            http_client=http_client,
            parser=parser,
        )
    if connector == "epe_open_files":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            uf=str(parameters.get("uf") or ""),
            competence_year=str(parameters.get("competence_year") or "2024"),
            max_rows=int(parameters.get("max_rows") or 8),
        )
    if connector == "anatel_dados_gov":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            uf=str(parameters.get("uf") or ""),
            competence_year=str(parameters.get("competence_year") or "2025"),
            competence_month=str(parameters.get("competence_month") or "11"),
            service=str(parameters.get("service") or "Banda Larga Fixa"),
            max_rows=int(parameters.get("max_rows") or 8),
        )
    if connector == "cnes_datasus_open":
        parameters = catalog.get("parameters") or {}
        return parser(
            fetched.body,
            uf=str(parameters.get("uf") or ""),
            codigo_uf=str(parameters.get("codigo_uf") or ""),
            competence=str(
                parameters.get("competence") or catalog.get("competence") or "as_published"
            ),
            max_rows=int(parameters.get("max_rows") or 8),
        )
    if connector == "siconfi_statement":
        return parser(fetched.body, dataset=str(catalog.get("dataset") or "RREO"))
    return parser(fetched.body)


def _parse_bcb_sgs_allowlist(
    fetched: OfficialHttpResponse,
    *,
    catalog: dict,
    http_client: OfficialHttpClient | None,
    parser,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    parameters = catalog.get("parameters") or {}
    allowlist = [int(item) for item in (parameters.get("series_allowlist") or [])]
    if not allowlist:
        raise ConflictError("BCB SGS connector requires series_allowlist")
    series_meta = parameters.get("series_meta") or {}
    ultimos = int(parameters.get("ultimos") or 3)
    primary_id = int(parameters.get("series_id") or allowlist[0])
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    timeout = get_settings().official_http_timeout_seconds
    for series_id in allowlist:
        meta = series_meta.get(str(series_id)) or series_meta.get(series_id) or {}
        label = str(meta.get("label") or f"SGS_{series_id}")
        unit = str(meta.get("unit") or "INDEX_POINTS")
        if series_id == primary_id:
            body = fetched.body
        else:
            if http_client is None:
                raise ConflictError("BCB allowlist secondary series require HTTP client")
            url = (
                "https://api.bcb.gov.br/dados/serie/"
                f"bcdata.sgs.{series_id}/dados/ultimos/{ultimos}?formato=json"
            )
            secondary = http_client.fetch(url, timeout=timeout)
            if secondary.status_code >= 400 or not secondary.body:
                raise ConflictError(f"BCB SGS series {series_id} download failed")
            body = secondary.body
        part_silver, part_quarantined = parser(
            body,
            series_id=series_id,
            series_label=label,
            unit=unit,
            allowlist=allowlist,
        )
        silver.extend(part_silver)
        quarantined.extend(part_quarantined)
    return silver, quarantined


def _bcb_olinda_expectativas_url(
    *,
    indicator: str,
    max_rows: int,
    base_calculo: int = 1,
    indicator_detalhe: str | None = None,
) -> str:
    encoded = quote(str(indicator).strip(), safe="")
    top = max(1, int(max_rows or 8))
    base = int(base_calculo)
    detalhe = str(indicator_detalhe or "").strip()
    if detalhe:
        enc_det = quote(detalhe, safe="")
        filter_clause = (
            f"Indicador%20eq%20%27{encoded}%27%20and%20"
            f"IndicadorDetalhe%20eq%20%27{enc_det}%27%20and%20"
            f"baseCalculo%20eq%20{base}"
        )
        select = "Indicador,IndicadorDetalhe,Data,DataReferencia,Mediana,Media,baseCalculo"
    else:
        filter_clause = f"Indicador%20eq%20%27{encoded}%27%20and%20baseCalculo%20eq%20{base}"
        select = "Indicador,Data,DataReferencia,Mediana,Media,baseCalculo"
    return (
        "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
        f"ExpectativasMercadoAnuais?$top={top}&$format=json&"
        f"$filter={filter_clause}&"
        "$orderby=Data%20desc,DataReferencia%20asc&"
        f"$select={select}"
    )


def _parse_bcb_olinda_expectativas_allowlist(
    fetched: OfficialHttpResponse,
    *,
    catalog: dict,
    http_client: OfficialHttpClient | None,
    parser,
) -> tuple[list[dict], list[tuple[dict, str]]]:
    parameters = catalog.get("parameters") or {}
    allowlist = [
        str(item).strip()
        for item in (parameters.get("indicator_allowlist") or [])
        if str(item).strip()
    ]
    if not allowlist:
        raise ConflictError("BCB OLINDA Expectativas requires indicator_allowlist")
    max_rows = int(parameters.get("max_rows") or 8)
    value_field = str(parameters.get("value_field") or "Mediana")
    indicator_units = parameters.get("indicator_units") or {}
    default_base = int(parameters.get("base_calculo") or 1)
    indicator_base_calculo = parameters.get("indicator_base_calculo") or {}
    indicator_detalhe = parameters.get("indicator_detalhe") or {}
    primary = str(parameters.get("primary_indicator") or allowlist[0]).strip()
    silver: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    timeout = get_settings().official_http_timeout_seconds
    for indicator in allowlist:
        base_calculo = int(indicator_base_calculo.get(indicator, default_base))
        detalhes = _normalize_indicator_detalhes(indicator_detalhe.get(indicator))
        for index, detalhe in enumerate(detalhes):
            use_primary_body = indicator == primary and index == 0 and len(detalhes) == 1
            if use_primary_body:
                body = fetched.body
            else:
                if http_client is None:
                    raise ConflictError(
                        "BCB Expectativas secondary indicators require HTTP client"
                    )
                url = _bcb_olinda_expectativas_url(
                    indicator=indicator,
                    max_rows=max_rows,
                    base_calculo=base_calculo,
                    indicator_detalhe=detalhe or None,
                )
                secondary = http_client.fetch(url, timeout=timeout)
                if secondary.status_code >= 400 or not secondary.body:
                    detail_label = f"/{detalhe}" if detalhe else ""
                    raise ConflictError(
                        f"BCB Expectativas indicator {indicator}{detail_label} download failed"
                    )
                body = secondary.body
            part_silver, part_quarantined = parser(
                body,
                indicator_allowlist=[indicator],
                max_rows=max_rows,
                value_field=value_field,
                indicator_units=indicator_units,
            )
            silver.extend(part_silver)
            quarantined.extend(part_quarantined)
    return silver, quarantined


def _normalize_indicator_detalhes(raw: object) -> list[str]:
    """Accept a single detalhe string or a list of detalhes; empty means no filter."""
    if raw is None:
        return [""]
    if isinstance(raw, (list, tuple)):
        values = [str(item).strip() for item in raw if str(item).strip()]
        return values or [""]
    text = str(raw).strip()
    return [text] if text else [""]


def _fetch_mg_dims(
    *,
    client: OfficialHttpClient | None,
    catalog: dict,
    timeout: float,
) -> tuple[bytes, bytes]:
    parameters = catalog.get("parameters") or {}
    municipio_url = str(parameters.get("municipio_endpoint") or "")
    tempo_url = str(parameters.get("tempo_endpoint") or "")
    if client is None or not municipio_url or not tempo_url:
        raise ConflictError("MG state connector requires municipio and tempo dimension endpoints")
    municipio = client.fetch(municipio_url, timeout=timeout)
    tempo = client.fetch(tempo_url, timeout=timeout)
    if municipio.status_code >= 400 or not municipio.body:
        raise ConflictError("MG municipio dimension download failed")
    if tempo.status_code >= 400 or not tempo.body:
        raise ConflictError("MG tempo dimension download failed")
    return municipio.body, tempo.body


def _ibge_lookup(session: Session, *, context: AccessContext) -> dict[tuple[str, str], str]:
    lookup: dict[tuple[str, str], str] = {}
    rows = session.scalars(
        select(DataLoadRow)
        .join(DataLoadRun, DataLoadRow.run_id == DataLoadRun.id)
        .where(
            DataLoadRun.tenant_id == context.tenant_id,
            DataLoadRun.territory_id == context.territory_id,
            DataLoadRun.source_id == "SICONFI-ENTES",
            DataLoadRow.layer == "silver",
        )
    )
    for row in rows:
        payload = row.payload or {}
        code = str(payload.get("ibgeCode") or "")
        if not code:
            continue
        name = str(
            payload.get("territoryName") or payload.get("ente") or payload.get("placeName") or ""
        )
        uf = str(payload.get("uf") or "")
        lookup[(normalize_place(name), normalize_place(uf))] = code
    return lookup


def _fetch_source(
    client: OfficialHttpClient,
    *,
    catalog: dict,
    connector: str,
    endpoint: str,
    timeout: float,
    session: Session,
    context: AccessContext,
    source_id: str,
) -> OfficialHttpResponse:
    if connector == "official_document":
        return _fetch_document(client, catalog=catalog, timeout=timeout)
    if connector == "siconfi_statement":
        return _fetch_siconfi_statement(
            client,
            catalog=catalog,
            timeout=timeout,
            session=session,
            context=context,
            source_id=source_id,
        )
    resolved = endpoint
    if connector == "tesouro_monthly_csv":
        resolved = resolve_fpm_endpoint(catalog) or endpoint
    if connector == "state_ac_transparencia_json":
        return _fetch_ac_transparencia_json(client, catalog=catalog, timeout=timeout)
    if connector == "state_pi_repasseweb_html":
        return _fetch_pi_repasseweb_html(client, catalog=catalog, timeout=timeout)
    return _fetch_pages(client, endpoint=resolved, connector=connector, timeout=timeout)


def _fetch_ac_transparencia_json(
    client: OfficialHttpClient,
    *,
    catalog: dict,
    timeout: float,
) -> OfficialHttpResponse:
    parameters = catalog.get("parameters") or {}
    endpoint = str(catalog.get("endpoint") or "")
    page_url = str(
        parameters.get("csrf_page_url")
        or catalog.get("official_url")
        or "https://transparencia.ac.gov.br/conteudo/repasse-aos-municipios-2"
    )
    competence = str(parameters.get("competence") or catalog.get("competence") or "2025-01")[:7]
    year, month = competence.split("-") if "-" in competence else ("2025", "01")
    form_data = {
        "tipo": "json",
        "ano": year,
        "mes": str(int(month)),
        "municipio": "",
    }
    return client.fetch_csrf_form_post(
        page_url=page_url,
        post_url=endpoint,
        form_data=form_data,
        timeout=timeout,
    )


def _fetch_pi_repasseweb_html(
    client: OfficialHttpClient,
    *,
    catalog: dict,
    timeout: float,
) -> OfficialHttpResponse:
    parameters = catalog.get("parameters") or {}
    page_url = str(
        catalog.get("endpoint")
        or "https://webas.sefaz.pi.gov.br/repasseweb/faces/views/repasseMunicipios.xhtml"
    )
    home_url = str(
        parameters.get("home_url")
        or catalog.get("official_url")
        or "https://webas.sefaz.pi.gov.br/repasseweb/"
    )
    competence = str(parameters.get("competence") or catalog.get("competence") or "2025-01")[:7]
    year, month = competence.split("-") if "-" in competence else ("2025", "01")
    tax = str(parameters.get("tax") or "IPVA").strip().upper()
    tax_code = "2" if tax == "ICMS" else "1"
    date_start = f"01/{month}/{year}"
    # Inclusive end-of-month day for short months is handled by official UI; use 31.
    date_end = f"31/{month}/{year}"
    return client.fetch_primefaces_datatable(
        home_url=home_url,
        page_url=page_url,
        tax_code=tax_code,
        year=year,
        date_start=date_start,
        date_end=date_end,
        rows=int(parameters.get("rows") or 1000),
        timeout=timeout,
    )


def _fetch_document(
    client: OfficialHttpClient, *, catalog: dict, timeout: float
) -> OfficialHttpResponse:
    urls = [str(catalog.get("endpoint") or "")]
    urls.extend(str(url) for url in catalog.get("alternate_endpoints") or [])
    last_error: Exception | None = None
    last_response: OfficialHttpResponse | None = None
    for url in urls:
        if not url:
            continue
        try:
            response = client.fetch(url, timeout=timeout)
        except Exception as exc:  # noqa: BLE001 - document fetch tries alternate official URLs
            last_error = exc
            continue
        last_response = response
        if response.status_code < 400 and response.body:
            return response
    if last_response is not None:
        return last_response
    if last_error is not None:
        raise last_error
    raise ConflictError("Official document endpoint is missing")


def _fetch_siconfi_statement(
    client: OfficialHttpClient,
    *,
    catalog: dict,
    timeout: float,
    session: Session,
    context: AccessContext,
    source_id: str,
) -> OfficialHttpResponse:
    settings = get_settings()
    started = time.perf_counter()
    parameters = catalog.get("parameters") or {}
    max_entes = clamp_max_entes(
        int(parameters.get("max_entes_per_run") or 1),
        hard_cap=settings.official_max_entes_hard_cap,
    )
    query = dict(parameters.get("query") or {})
    partition_key = statement_partition_key(
        competence=str(catalog.get("competence") or "current"),
        query=query,
    )
    disk_free = assert_datalake_space(
        root=Path(settings.datalake_root),
        min_free_bytes=settings.datalake_min_free_bytes,
    )
    checkpoint = session.scalar(
        select(IngestCheckpoint).where(
            IngestCheckpoint.tenant_id == context.tenant_id,
            IngestCheckpoint.territory_id == context.territory_id,
            IngestCheckpoint.source_id == source_id,
            IngestCheckpoint.partition_key == partition_key,
        )
    )
    if checkpoint is not None and checkpoint.status == "COMPLETE":
        raise ConflictError(
            f"backfill partition {partition_key} already COMPLETE; "
            "refuse silent restart without explicit allow_restart"
        )
    if checkpoint is not None and str(checkpoint.cursor).isdigit():
        skip = int(checkpoint.cursor)
    else:
        skip = 0
    lookup = _ibge_lookup(session, context=context)
    codes = sorted({code for code in lookup.values() if code})
    if not codes:
        default_ente = str(query.get("id_ente") or "3304557")
        codes = [default_ente]
    selected, skip, exhausted = select_entes_slice(codes, skip=skip, max_entes=max_entes)
    items: list[dict] = []
    base = str(catalog.get("endpoint") or "")
    last = client.fetch(base, timeout=timeout)
    bytes_fetched = len(last.body)
    for code in selected:
        params = {**query, "id_ente": code}
        suffix = "&".join(
            f"{key}={value}" for key, value in params.items() if value not in (None, "")
        )
        url = f"{base}?{suffix}" if suffix else base
        last = client.fetch(url, timeout=timeout)
        bytes_fetched += len(last.body)
        if last.status_code >= 400:
            continue
        try:
            payload = json.loads(last.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        page_items = payload.get("items") if isinstance(payload, dict) else payload
        if isinstance(page_items, list):
            items.extend(item for item in page_items if isinstance(item, dict))
    next_offset = skip + len(selected) if not exhausted else skip
    status = checkpoint_status_after_slice(next_offset=next_offset, total_entes=len(codes))
    if exhausted:
        status = "COMPLETE"
        next_offset = len(codes)
    duration_ms = int((time.perf_counter() - started) * 1000)
    metrics = build_backfill_metrics(
        offset=next_offset,
        last_ente=selected[-1] if selected else None,
        entes_this_run=len(selected),
        item_count=len(items),
        duration_ms=duration_ms,
        bytes_fetched=bytes_fetched,
        disk_free_bytes=disk_free,
        total_entes=len(codes),
        max_entes_per_run=max_entes,
    )
    if checkpoint is None:
        session.add(
            IngestCheckpoint(
                tenant_id=context.tenant_id,
                territory_id=context.territory_id,
                source_id=source_id,
                partition_key=partition_key,
                cursor=str(next_offset),
                status=status,
                metrics=metrics,
                updated_at=datetime.now(UTC),
            )
        )
    else:
        checkpoint.cursor = str(next_offset)
        checkpoint.status = status
        checkpoint.metrics = metrics
        checkpoint.updated_at = datetime.now(UTC)
    if exhausted and not items:
        merged = json.dumps({"items": []}, ensure_ascii=False).encode("utf-8")
        return OfficialHttpResponse(
            url=last.url,
            status_code=200,
            body=merged,
            etag=last.etag,
            last_modified=last.last_modified,
            content_type="application/json",
        )
    merged = json.dumps({"items": items}, ensure_ascii=False).encode("utf-8")
    return OfficialHttpResponse(
        url=last.url,
        status_code=last.status_code if items or last.status_code < 400 else last.status_code,
        body=merged if items else last.body,
        etag=last.etag,
        last_modified=last.last_modified,
        content_type="application/json",
    )


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
    body = {
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
    if str(catalog.get("connector") or "") == RFB_CONNECTOR:
        body["rfbReadiness"] = build_rfb_readiness(catalog.get("parameters"))
    return body
