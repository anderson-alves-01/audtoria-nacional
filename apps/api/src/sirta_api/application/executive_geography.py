"""Read published IBGE municipal lines for the executive map."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import GoldOfficial, GoldOfficialLine
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.executive_geography import (
    EXECUTIVE_MAP_SOURCES,
    SOURCE_LABELS,
    UF_BY_CODE,
    assemble_geography,
)


def list_executive_geography(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    uf_code = func.substr(GoldOfficialLine.ibge_code, 1, 2)
    label = func.coalesce(
        GoldOfficialLine.payload["variableName"].astext,
        GoldOfficialLine.source_id,
    )
    competence = func.substr(
        func.coalesce(
            GoldOfficialLine.payload["competence"].astext,
            GoldOfficial.competence,
        ),
        1,
        4,
    )
    rows = session.execute(
        select(
            GoldOfficialLine.source_id,
            uf_code,
            label,
            GoldOfficialLine.unit,
            competence,
            func.sum(GoldOfficialLine.value),
            func.count(func.distinct(GoldOfficialLine.ibge_code)),
        )
        .join(GoldOfficial, GoldOfficialLine.gold_id == GoldOfficial.id)
        .where(
            GoldOfficial.tenant_id == context.tenant_id,
            GoldOfficial.territory_id == context.territory_id,
            GoldOfficial.published.is_(True),
            GoldOfficial.source_id.in_(EXECUTIVE_MAP_SOURCES),
            GoldOfficialLine.value.is_not(None),
            func.length(GoldOfficialLine.ibge_code) == 7,
        )
        .group_by(
            GoldOfficialLine.source_id,
            uf_code,
            label,
            GoldOfficialLine.unit,
            competence,
        )
    ).all()
    groups = []
    for source_id, code, measure, unit, year, total, municipalities in rows:
        if str(code or "") not in UF_BY_CODE or total is None:
            continue
        groups.append(
            {
                "sourceId": source_id,
                "ufCode": str(code),
                "label": str(measure or SOURCE_LABELS.get(source_id, source_id)),
                "unit": str(unit or "UNIT"),
                "competence": str(year or "")[:4],
                "total": float(total),
                "municipalityCount": int(municipalities or 0),
            }
        )
    return assemble_geography(groups)
