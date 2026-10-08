"""Read the state summary of published municipal money.

The map does not scan statement lines. A refresh writes one Gold row per
state, source and year, and the next refresh replaces that snapshot.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import GoldFinanceStateSummary, GoldOfficial, GoldOfficialLine
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.dashboard_charts import statement_revenue_account_codes
from sirta_api.domain.executive_geography import UF_BY_CODE
from sirta_api.domain.finance_geography import (
    FINANCE_MAP_SOURCES,
    aggregate_finance_geography,
    finance_summary_records,
    recovery_reading,
    replace_summary_snapshot,
    view_from_summary,
)


def list_finance_geography(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    rows = session.scalars(
        select(GoldFinanceStateSummary).where(
            GoldFinanceStateSummary.tenant_id == context.tenant_id,
            GoldFinanceStateSummary.territory_id == context.territory_id,
        )
    ).all()
    view = view_from_summary([_group(row) for row in rows])
    view["recovery"] = recovery_reading(view)
    return view


def refresh_finance_state_summary(session: Session, *, tenant_id: UUID, territory_id: UUID) -> int:
    """Replace the stored state totals for one tenant and territory."""
    cells = _fpm_cells(session, tenant_id, territory_id) + _statement_cells(
        session, tenant_id, territory_id
    )
    incoming = finance_summary_records(aggregate_finance_geography(cells))
    current = {
        (row.source_id, row.uf_code, row.competence): row
        for row in session.scalars(
            select(GoldFinanceStateSummary).where(
                GoldFinanceStateSummary.tenant_id == tenant_id,
                GoldFinanceStateSummary.territory_id == territory_id,
            )
        ).all()
    }
    snapshot = replace_summary_snapshot(current, incoming)
    session.execute(
        delete(GoldFinanceStateSummary).where(
            GoldFinanceStateSummary.tenant_id == tenant_id,
            GoldFinanceStateSummary.territory_id == territory_id,
        )
    )
    refreshed_at = datetime.now(UTC)
    for row in snapshot.values():
        session.add(
            GoldFinanceStateSummary(
                id=uuid4(),
                tenant_id=tenant_id,
                territory_id=territory_id,
                source_id=row["sourceId"],
                uf_code=row["ufCode"],
                competence=row["competence"],
                label=row["label"],
                unit=row["unit"],
                total=row["total"],
                municipality_count=row["municipalityCount"],
                refreshed_at=refreshed_at,
            )
        )
    return len(snapshot)


def refresh_published_finance_summaries(session: Session) -> int:
    pairs = session.execute(
        select(GoldOfficial.tenant_id, GoldOfficial.territory_id)
        .where(
            GoldOfficial.published.is_(True),
            GoldOfficial.source_id.in_(FINANCE_MAP_SOURCES),
        )
        .distinct()
    ).all()
    total = 0
    for tenant_id, territory_id in pairs:
        total += refresh_finance_state_summary(
            session, tenant_id=tenant_id, territory_id=territory_id
        )
    return total


def _group(row: GoldFinanceStateSummary) -> dict:
    return {
        "sourceId": row.source_id,
        "ufCode": row.uf_code,
        "label": row.label,
        "unit": row.unit,
        "competence": row.competence,
        "total": float(row.total),
        "municipalityCount": row.municipality_count,
    }


def _fpm_cells(session: Session, tenant_id: UUID, territory_id: UUID) -> list[dict]:
    uf_code = func.substr(GoldOfficialLine.ibge_code, 1, 2)
    year = _year()
    modality = GoldOfficialLine.payload["modality"].astext
    rows = session.execute(
        select(
            uf_code,
            year,
            func.sum(GoldOfficialLine.value),
            func.count(func.distinct(GoldOfficialLine.ibge_code)),
        )
        .join(GoldOfficial, GoldOfficialLine.gold_id == GoldOfficial.id)
        .where(
            GoldOfficial.tenant_id == tenant_id,
            GoldOfficial.territory_id == territory_id,
            GoldOfficial.published.is_(True),
            GoldOfficial.source_id == "TESOURO-FPM-VALORES",
            GoldOfficialLine.value.is_not(None),
            func.length(GoldOfficialLine.ibge_code) == 7,
            or_(modality.is_(None), modality == "", modality == "FPM_RECEIVED"),
        )
        .group_by(uf_code, year)
    ).all()
    cells = []
    for code, year_value, total, count in rows:
        cell = _cell("TESOURO-FPM-VALORES", code, "", "", year_value, total, count)
        if cell:
            cells.append(cell)
    return cells


def _statement_cells(session: Session, tenant_id: UUID, territory_id: UUID) -> list[dict]:
    uf_code = func.substr(GoldOfficialLine.ibge_code, 1, 2)
    year = _year()
    account = GoldOfficialLine.payload["account"].astext
    column = GoldOfficialLine.payload["column"].astext
    rows = session.execute(
        select(
            GoldOfficial.source_id,
            uf_code,
            account,
            column,
            year,
            func.sum(GoldOfficialLine.value),
            func.count(func.distinct(GoldOfficialLine.ibge_code)),
        )
        .join(GoldOfficial, GoldOfficialLine.gold_id == GoldOfficial.id)
        .where(
            GoldOfficial.tenant_id == tenant_id,
            GoldOfficial.territory_id == territory_id,
            GoldOfficial.published.is_(True),
            GoldOfficial.source_id.in_(("SICONFI-RREO", "SICONFI-DCA")),
            account.in_(tuple(statement_revenue_account_codes())),
            GoldOfficialLine.value.is_not(None),
            func.length(GoldOfficialLine.ibge_code) == 7,
        )
        .group_by(GoldOfficial.source_id, uf_code, account, column, year)
    ).all()
    cells = []
    for source_id, code, account_value, column_value, year_value, total, count in rows:
        cell = _cell(source_id, code, account_value, column_value, year_value, total, count)
        if cell:
            cells.append(cell)
    return cells


def _year():
    return func.substr(
        func.coalesce(
            GoldOfficialLine.payload["competence"].astext,
            GoldOfficial.competence,
        ),
        1,
        4,
    )


def _cell(source_id, code, account, column, year, total, count) -> dict:
    if str(code or "") not in UF_BY_CODE or total is None:
        return {}
    return {
        "sourceId": source_id,
        "ufCode": str(code),
        "account": str(account or ""),
        "column": str(column or ""),
        "unit": "BRL",
        "competence": str(year or "")[:4],
        "total": float(total),
        "municipalityCount": int(count or 0),
    }
