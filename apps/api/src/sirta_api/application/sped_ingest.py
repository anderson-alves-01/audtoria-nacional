"""Upload, validate and read the SPED NF-e UF x CFOP consolidated workbook.

The load is idempotent by tenant, checksum and layout. Nothing becomes a tax credit and the
R$ column is an estimated allocation that is never summed across operations.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import DataLoadRow, DataLoadRun, SpedOperationFact
from sirta_api.adapters.ingest.catalog_loader import catalog_source
from sirta_api.adapters.ingest.parsers import landing_dir, sha256_bytes, write_landing
from sirta_api.adapters.ingest.sped_xlsx import SpedLayoutError, parse_sped_workbook
from sirta_api.application.audit import record_audit
from sirta_api.application.indicator_reliability import SPED_INDICATORS, reliability_for
from sirta_api.application.source_ingest import _load_source
from sirta_api.config import get_settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import assert_ingest_allowed
from sirta_api.domain.errors import ForbiddenError, NotVisibleError, ValidationFailedError
from sirta_api.domain.sped_operations import (
    DIRECTION_SENT,
    OPERATIONS,
    SPED_BANNER,
    SPED_COMPETENCE,
    SPED_LAYOUT_VERSION,
    SPED_SOURCE_ID,
    SPED_VALUE_KIND,
    TRANSFER_OPERATION,
    UFS,
    YEARS,
    SpedWorkbook,
    classify_cfop_sirta,
    reconcile,
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_PAGE_SIZE = 1000
INSERT_CHUNK = 5000
FORMULA = (
    "Valor estimado do par UF–CFOP–ano = valor nacional do CFOP no ano × quantidade da UF no "
    "CFOP/ano ÷ soma das quantidades das UFs no CFOP/ano. Quantidade é observada. O valor em R$ "
    "é rateio estimado, não é valor fiscal efetivo e não é somado entre operações."
)


def _run_body(run: DataLoadRun, *, replay: bool, report: dict | None = None) -> dict:
    return {
        "sourceId": run.source_id,
        "runId": str(run.id),
        "status": run.status,
        "replay": replay,
        "published": run.published,
        "homologated": False,
        "createsTaxCredit": False,
        "layoutVersion": run.layout_version,
        "competence": run.competence,
        "checksum": run.checksum,
        "receivedCount": run.received_count,
        "silverCount": run.silver_count,
        "quarantinedCount": run.quarantined_count,
        "valueKind": SPED_VALUE_KIND,
        "banner": SPED_BANNER,
        "reconciliation": report,
    }


def _report_payload(report) -> dict:
    return {
        "ok": report.ok,
        "errors": report.errors,
        "warnings": report.warnings,
        "seriesRows": report.series_rows,
        "baseLines": report.base_rows,
        "baseFacts": report.base_facts,
        "consolidatedCells": report.consolidated_cells,
        "maxValueDifference": str(report.max_value_difference),
        "classificationMismatches": report.classification_mismatches,
        "transferQuantity": report.transfer_quantity,
        "transferUnconfirmedQuantity": report.transfer_unconfirmed_quantity,
    }


def _fact_rows(workbook: SpedWorkbook, *, run_id, context: AccessContext, now) -> list[dict]:
    common = {
        "run_id": run_id,
        "tenant_id": context.tenant_id,
        "territory_id": context.territory_id,
        "created_at": now,
    }
    rows = [
        {
            **common,
            "id": uuid4(),
            "level": "SERIE",
            "ano": item.year,
            "uf": item.uf,
            "operacao": item.operation,
            "cfop": "",
            "quantidade": item.quantity,
            "valor_estimado": item.estimated_value,
            "comparable_quantity": item.comparable_quantity,
            "comparable_share": item.comparable_share,
            "cfop_pairs": item.cfop_pairs,
            "covered_quantity": item.covered_quantity,
            "direcao": _workbook_direction(item.operation),
        }
        for item in workbook.serie
    ]
    rows.extend(
        {
            **common,
            "id": uuid4(),
            "level": "CFOP",
            "ano": item.year,
            "uf": item.uf,
            "operacao": item.operation,
            "cfop": item.cfop,
            "quantidade": item.quantity,
            "valor_estimado": item.estimated_value,
            "comparable_quantity": None,
            "comparable_share": None,
            "cfop_pairs": None,
            "covered_quantity": None,
            "direcao": _workbook_direction(item.operation),
        }
        for item in workbook.base
    )
    return rows


def _workbook_direction(operation: str) -> str | None:
    """The workbook only has outbound CFOPs (5, 6, 7), so its transfers are REMETIDA.

    Received transfers (1.15x and 2.15x) are not in the workbook; they would need a separate,
    explicitly authorized load of the official history.
    """
    return DIRECTION_SENT if operation == TRANSFER_OPERATION else None


def ingest_sped_upload(
    session: Session, *, context: AccessContext, source_id: str, body: bytes
) -> dict:
    if context.role.value != "tech_admin":
        raise ForbiddenError("Only a technical administrator may run data loads")
    if source_id != SPED_SOURCE_ID:
        raise NotVisibleError()
    source = _load_source(session, context=context, source_id=source_id)
    assert_ingest_allowed(
        source_role=source.source_role,
        access_classification=source.access_classification,
        status=source.status,
        fixture_kind=source.fixture_kind,
    )
    if not body:
        raise ValidationFailedError("O arquivo enviado está vazio.")
    if len(body) > MAX_UPLOAD_BYTES:
        raise ValidationFailedError("O arquivo excede o tamanho máximo aceito.")
    digest = sha256_bytes(body)
    route = f"/v1/data-sources/{source_id}/upload"
    existing = session.scalar(
        select(DataLoadRun).where(
            DataLoadRun.tenant_id == context.tenant_id,
            DataLoadRun.checksum == digest,
            DataLoadRun.layout_version == SPED_LAYOUT_VERSION,
        )
    )
    if existing is not None:
        record_audit(
            session,
            context=context,
            action="sped.upload.replay",
            route=route,
            outcome="allowed",
            resource_type="data_load_run",
            resource_id=existing.id,
        )
        session.flush()
        return _run_body(existing, replay=True)
    try:
        workbook = parse_sped_workbook(body)
    except SpedLayoutError as exc:
        raise ValidationFailedError(str(exc)) from exc
    report = reconcile(workbook)
    now = datetime.now(UTC)
    catalog = catalog_source(source_id) or {}
    directory = landing_dir(
        root=Path(get_settings().datalake_root),
        source_id=source_id,
        dataset=str(catalog.get("dataset") or source_id),
        extracted_at=now,
        checksum=digest,
    )
    write_landing(
        directory=directory,
        body=body,
        manifest={
            "sourceId": source_id,
            "dataset": catalog.get("dataset"),
            "officialUrl": catalog.get("official_url"),
            "extractedAtUtc": now.isoformat(),
            "sha256": digest,
            "sizeBytes": len(body),
            "layoutVersion": SPED_LAYOUT_VERSION,
            "competence": SPED_COMPETENCE,
            "purpose": catalog.get("purpose"),
            "valueKind": SPED_VALUE_KIND,
            "origin": "operator_upload",
        },
    )
    received = len(workbook.serie) + len(workbook.base)
    run = DataLoadRun(
        id=uuid4(),
        tenant_id=context.tenant_id,
        territory_id=context.territory_id,
        source_id=source_id,
        layout_version=SPED_LAYOUT_VERSION,
        competence=SPED_COMPETENCE,
        checksum=digest,
        status="VALIDATED" if report.ok else "QUARANTINED",
        received_count=received,
        silver_count=received if report.ok else 0,
        quarantined_count=0 if report.ok else received,
        published=False,
        created_at=now,
    )
    session.add(run)
    session.flush()
    session.add(
        DataLoadRow(
            id=uuid4(),
            run_id=run.id,
            row_id="reconciliation",
            layer="manifest",
            status="VALIDATED" if report.ok else "QUARANTINED",
            payload=_report_payload(report),
            reason=None if report.ok else "reconciliation failed",
        )
    )
    if report.ok:
        rows = _fact_rows(workbook, run_id=run.id, context=context, now=now)
        for start in range(0, len(rows), INSERT_CHUNK):
            session.execute(insert(SpedOperationFact), rows[start : start + INSERT_CHUNK])
    record_audit(
        session,
        context=context,
        action="sped.upload" if report.ok else "sped.upload.quarantined",
        route=route,
        outcome="allowed" if report.ok else "quarantined",
        resource_type="data_load_run",
        resource_id=run.id,
    )
    session.flush()
    return _run_body(run, replay=False, report=_report_payload(report))


def _check_filters(
    *, ano: int | None, uf: str | None, operacao: str | None, cfop: str | None, level: str
) -> None:
    if level not in {"SERIE", "CFOP"}:
        raise ValidationFailedError("level deve ser SERIE ou CFOP.")
    if ano is not None and ano not in YEARS:
        raise ValidationFailedError("ano deve estar entre 2021 e 2025.")
    if uf is not None and uf not in UFS:
        raise ValidationFailedError("uf desconhecida.")
    if operacao is not None and operacao not in OPERATIONS:
        raise ValidationFailedError("operacao desconhecida.")
    if cfop is not None and (len(cfop) != 4 or not cfop.isdigit()):
        raise ValidationFailedError("cfop deve ter 4 dígitos.")


def _money(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def list_sped_operations(
    session: Session,
    *,
    context: AccessContext,
    level: str = "SERIE",
    ano: int | None = None,
    uf: str | None = None,
    operacao: str | None = None,
    cfop: str | None = None,
    page: int = 1,
    page_size: int = 200,
) -> dict:
    context.ensure_fiscal_read()
    _check_filters(ano=ano, uf=uf, operacao=operacao, cfop=cfop, level=level)
    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
    run = session.scalar(
        select(DataLoadRun)
        .where(
            DataLoadRun.tenant_id == context.tenant_id,
            DataLoadRun.territory_id == context.territory_id,
            DataLoadRun.source_id == SPED_SOURCE_ID,
            DataLoadRun.status == "VALIDATED",
        )
        .order_by(DataLoadRun.created_at.desc())
        .limit(1)
    )
    body: dict = {
        "sourceId": SPED_SOURCE_ID,
        "valueKind": SPED_VALUE_KIND,
        "banner": SPED_BANNER,
        "formula": FORMULA,
        "homologated": False,
        "published": False,
        "createsTaxCredit": False,
        "reliability": reliability_for(SPED_INDICATORS),
        "level": level,
        "page": page,
        "pageSize": page_size,
        "total": 0,
        "years": list(YEARS),
        "operations": list(OPERATIONS),
        "ufs": list(UFS),
        "run": None,
        "items": [],
    }
    if run is not None:
        conditions = [
            SpedOperationFact.run_id == run.id,
            SpedOperationFact.tenant_id == context.tenant_id,
            SpedOperationFact.territory_id == context.territory_id,
            SpedOperationFact.level == level,
        ]
        if ano is not None:
            conditions.append(SpedOperationFact.ano == ano)
        if uf is not None:
            conditions.append(SpedOperationFact.uf == uf)
        if operacao is not None:
            conditions.append(SpedOperationFact.operacao == operacao)
        if cfop is not None and level == "CFOP":
            conditions.append(SpedOperationFact.cfop == cfop)
        total = session.scalar(
            select(func.count()).select_from(SpedOperationFact).where(*conditions)
        )
        facts = session.scalars(
            select(SpedOperationFact)
            .where(*conditions)
            .order_by(
                SpedOperationFact.ano,
                SpedOperationFact.uf,
                SpedOperationFact.operacao,
                SpedOperationFact.cfop,
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        body["total"] = int(total or 0)
        body["run"] = {
            "runId": str(run.id),
            "checksum": run.checksum,
            "layoutVersion": run.layout_version,
            "competence": run.competence,
            "loadedAt": run.created_at.isoformat(),
            "receivedCount": run.received_count,
        }
        body["items"] = [_fact_item(fact, level=level) for fact in facts]
    record_audit(
        session,
        context=context,
        action="sped_operacoes.list",
        route="/v1/sped-operacoes",
        outcome="allowed",
        resource_type="data_load_run",
        resource_id=run.id if run is not None else None,
    )
    return body


def _fact_item(fact: SpedOperationFact, *, level: str) -> dict:
    item = {
        "ano": fact.ano,
        "uf": fact.uf,
        "operacao": fact.operacao,
        "quantidade": fact.quantidade,
        "valorEstimado": _money(fact.valor_estimado),
    }
    if fact.operacao == TRANSFER_OPERATION:
        item["direcao"] = fact.direcao
    if level == "CFOP":
        item["cfop"] = fact.cfop
        if fact.operacao == TRANSFER_OPERATION:
            # Whether the official CFOP table lists this code as a transfer.
            item["classificacaoCfop"] = classify_cfop_sirta(fact.cfop).status
    else:
        item["comparableQuantity"] = fact.comparable_quantity
        item["comparableShare"] = _money(fact.comparable_share)
        item["cfopPairs"] = fact.cfop_pairs
        item["coveredQuantity"] = fact.covered_quantity
    return item
