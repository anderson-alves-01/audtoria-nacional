"""Read published municipal money grouped by state."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import GoldOfficial, GoldOfficialLine
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.dashboard_charts import statement_revenue_account_codes
from sirta_api.domain.executive_geography import UF_BY_CODE
from sirta_api.domain.finance_geography import aggregate_finance_geography


def list_finance_geography(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    cells = _fpm_cells(session, context) + _statement_cells(session, context)
    return aggregate_finance_geography(cells)


def _fpm_cells(session: Session, context: AccessContext) -> list[dict]:
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
            GoldOfficial.tenant_id == context.tenant_id,
            GoldOfficial.territory_id == context.territory_id,
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


def _statement_cells(session: Session, context: AccessContext) -> list[dict]:
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
            GoldOfficial.tenant_id == context.tenant_id,
            GoldOfficial.territory_id == context.territory_id,
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
