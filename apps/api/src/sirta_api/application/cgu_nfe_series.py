"""Read local CGU NF-e aggregates for the Simulador. No Postgres, no bronze, no PII."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.application.audit import record_audit
from sirta_api.application.indicator_reliability import reliability_for
from sirta_api.config import get_settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.cgu_nfe import (
    PROCESSING_VERSION,
    SIMULATOR_BANNER,
    SIMULATOR_FORMULA,
    SOURCE_ID,
    UFS,
    VALUE_KIND_OBSERVED,
    YEARS,
    coverage_of,
    requested_months,
    roll_year_uf,
    series_item,
)
from sirta_api.domain.errors import ValidationFailedError

MAX_PAGE_SIZE = 1000
CGU_INDICATORS = (
    "cgu_nfe_itens_uf_ano",
    "cgu_nfe_valor_itens_uf_ano",
    "simulador_imposto_apurado_dados_publicos",
)


def cgu_nfe_root() -> Path:
    return Path(get_settings().datalake_root) / "cgu-nfe"


def _empty_body(
    *,
    page: int,
    page_size: int,
    coverage: str,
    missing: list[str],
    processed: int = 0,
) -> dict:
    return {
        "sourceId": SOURCE_ID,
        "valueKind": VALUE_KIND_OBSERVED,
        "banner": SIMULATOR_BANNER,
        "formula": SIMULATOR_FORMULA,
        "homologated": False,
        "published": False,
        "createsTaxCredit": False,
        "reliability": reliability_for(CGU_INDICATORS),
        "coverage": coverage,
        "monthsProcessed": processed,
        "monthsMissing": missing,
        "page": page,
        "pageSize": page_size,
        "total": 0,
        "years": list(YEARS),
        "ufs": sorted(UFS),
        "run": None,
        "items": [],
    }


def list_cgu_nfe(
    session: Session,
    *,
    context: AccessContext,
    uf: str | None = None,
    ano: int | None = None,
    page: int = 1,
    page_size: int = 200,
    root: Path | None = None,
) -> dict:
    context.ensure_fiscal_read()
    if ano is not None and ano not in YEARS:
        raise ValidationFailedError("ano deve estar entre 2021 e 2025.")
    if uf is not None and uf not in UFS:
        raise ValidationFailedError("uf desconhecida.")
    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
    lake = root if root is not None else cgu_nfe_root()
    sqlite_path = lake / "cgu-nfe.sqlite"
    requested = requested_months()
    if not sqlite_path.is_file():
        body = _empty_body(
            page=page,
            page_size=page_size,
            coverage="AUSENTE",
            missing=requested,
        )
        record_audit(
            session,
            context=context,
            action="cgu_nfe.list",
            route="/v1/cgu-nfe",
            outcome="allowed",
            resource_type="cgu_nfe",
        )
        return body

    store = Store(lake)
    try:
        months = store.processed_months_for_version(PROCESSING_VERSION)
        coverage, missing = coverage_of(requested, months)
        if not months:
            body = _empty_body(
                page=page,
                page_size=page_size,
                coverage=coverage,
                missing=missing,
            )
        else:
            rows = roll_year_uf(
                item_rows=store.year_uf_item_rows(months),
                note_rows=store.year_uf_note_rows(months),
            )
            if uf is not None:
                rows = [row for row in rows if row.uf == uf]
            if ano is not None:
                rows = [row for row in rows if row.year == ano]
            items = [series_item(row) for row in rows]
            total = len(items)
            start = (page - 1) * page_size
            latest = store.latest_completed_run(PROCESSING_VERSION)
            body = _empty_body(
                page=page,
                page_size=page_size,
                coverage=coverage,
                missing=missing,
                processed=len(months),
            )
            body["total"] = total
            body["items"] = items[start : start + page_size]
            body["run"] = {
                "runId": latest["run_id"] if latest and latest["run_id"] else PROCESSING_VERSION,
                "layoutVersion": PROCESSING_VERSION,
                "competence": "2021-01..2025-12",
                "monthsProcessed": len(months),
                "loadedAt": latest["finished_at"] if latest else None,
            }
    finally:
        store.close()

    record_audit(
        session,
        context=context,
        action="cgu_nfe.list",
        route="/v1/cgu-nfe",
        outcome="allowed",
        resource_type="cgu_nfe",
    )
    return body
