from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.municipal_uploads import (
    get_municipal_uploads,
    municipal_upload_command_rejected,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/municipal-uploads")
def municipal_uploads_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> dict:
    return get_municipal_uploads(session, context=context, page=page, size=size)


@router.post("/v1/municipal-uploads")
def municipal_uploads_command_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> None:
    municipal_upload_command_rejected(session, context=context)
