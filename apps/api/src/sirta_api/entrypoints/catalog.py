from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.adapters.ingest.deps import get_official_http_client
from sirta_api.adapters.ingest.http_client import OfficialHttpClient
from sirta_api.application.catalog import dry_run_source, list_sources
from sirta_api.application.official_ingest import list_official_gold
from sirta_api.application.source_ingest import ingest_catalog_source, published_enrichment
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


@router.post("/v1/data-sources/{sourceId}/ingest")
def post_source_ingest(
    sourceId: str,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    http_client: OfficialHttpClient = Depends(get_official_http_client),
) -> dict:
    return ingest_catalog_source(
        session, context=context, source_id=sourceId, http_client=http_client
    )


@router.get("/v1/indicators/source-enrichment")
def get_source_enrichment(
    sourceId: str = Query(...),
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return published_enrichment(session, context=context, source_id=sourceId)


@router.get("/v1/indicators/official-gold")
def get_official_gold(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_official_gold(session, context=context)
