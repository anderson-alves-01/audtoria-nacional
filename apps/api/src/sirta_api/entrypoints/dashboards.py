from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.dashboards import get_dashboard, list_dashboards
from sirta_api.application.executive_geography import list_executive_geography
from sirta_api.application.official_ingest import list_official_gold_lines
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/dashboards")
def get_dashboards(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_dashboards(session, context=context)


@router.get("/v1/dashboards/executivo/geography")
def get_executive_geography(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_executive_geography(session, context=context)


@router.get("/v1/dashboards/{dashboardId}")
def get_dashboard_by_id(
    dashboardId: str,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return get_dashboard(session, context=context, dashboard_id=dashboardId)


@router.get("/v1/indicators/official-gold/lines")
def get_official_gold_lines(
    sourceId: str | None = None,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_official_gold_lines(session, context=context, source_id=sourceId)
