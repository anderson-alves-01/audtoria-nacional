from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.catalog import dry_run_source, list_sources
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/data-sources")
def get_data_sources(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_sources(session, context=context)


@router.post("/v1/data-sources/{sourceId}/dry-run")
def post_source_dry_run(
    sourceId: str,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return dry_run_source(session, context=context, source_id=sourceId)
