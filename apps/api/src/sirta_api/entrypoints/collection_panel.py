from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.collection_panel import get_collection_panel
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/collection")
def collection_panel_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return get_collection_panel(session, context=context)
